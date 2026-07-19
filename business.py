"""Gestão local simples de clientes e vendas para pequenos negócios."""
import argparse
import csv
import sqlite3
from datetime import date
from pathlib import Path

DB = Path.home() / ".agentos_business.db"


def connect(path=DB):
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY,name TEXT NOT NULL,phone TEXT DEFAULT '')")
    connection.execute("CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY,client_id INTEGER NOT NULL,description TEXT NOT NULL,amount REAL NOT NULL CHECK(amount >= 0),created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(client_id) REFERENCES clients(id))")
    columns = {row[1] for row in connection.execute("PRAGMA table_info(sales)")}
    if "paid" not in columns:
        connection.execute("ALTER TABLE sales ADD COLUMN paid INTEGER NOT NULL DEFAULT 1 CHECK(paid IN (0,1))")
    if "due_date" not in columns:
        connection.execute("ALTER TABLE sales ADD COLUMN due_date TEXT")
    if "paid_at" not in columns:
        connection.execute("ALTER TABLE sales ADD COLUMN paid_at TEXT")
    connection.commit()
    return connection


def export_csv(connection, path):
    rows = connection.execute("SELECT s.id,c.name,s.description,s.amount,s.created_at,CASE WHEN s.paid=1 THEN 'pago' ELSE 'pendente' END,s.due_date,s.paid_at FROM sales s JOIN clients c ON c.id=s.client_id ORDER BY s.id").fetchall()
    with open(path, "w", newline="", encoding="utf-8-sig") as output:
        writer = csv.writer(output)
        writer.writerow(("id", "cliente", "descricao", "valor", "data", "status", "vencimento", "recebido_em"))
        writer.writerows(rows)
    return len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="AgentOS Business Toolkit")
    parser.add_argument("--db", default=str(DB))
    commands = parser.add_subparsers(dest="cmd", required=True)
    client = commands.add_parser("cliente")
    client.add_argument("nome")
    client.add_argument("--telefone", default="")
    sale = commands.add_parser("venda")
    sale.add_argument("cliente", type=int)
    sale.add_argument("descricao")
    sale.add_argument("valor", type=float)
    sale.add_argument("--vencimento", help="data YYYY-MM-DD; registra a venda como pendente")
    commands.add_parser("clientes")
    commands.add_parser("vendas")
    commands.add_parser("resumo")
    commands.add_parser("pendentes")
    receive = commands.add_parser("receber", help="marca uma venda pendente como recebida")
    receive.add_argument("venda", type=int)
    export = commands.add_parser("exportar")
    export.add_argument("arquivo", nargs="?", default="vendas.csv")
    args = parser.parse_args(argv)
    connection = connect(args.db)
    try:
        if args.cmd == "cliente":
            cursor = connection.execute("INSERT INTO clients(name,phone) VALUES(?,?)", (args.nome, args.telefone))
            connection.commit()
            print(f"Cliente cadastrado com ID {cursor.lastrowid}")
        elif args.cmd == "venda":
            if args.vencimento:
                try:
                    date.fromisoformat(args.vencimento)
                except ValueError:
                    parser.error("vencimento inválido; use YYYY-MM-DD")
            paid = 0 if args.vencimento else 1
            connection.execute("INSERT INTO sales(client_id,description,amount,paid,due_date,paid_at) VALUES(?,?,?,?,?,CASE WHEN ?=1 THEN CURRENT_TIMESTAMP ELSE NULL END)", (args.cliente, args.descricao, args.valor, paid, args.vencimento, paid))
            connection.commit()
            print("Venda cadastrada" + (f" como pendente até {args.vencimento}" if args.vencimento else " como paga"))
        elif args.cmd == "clientes":
            for row in connection.execute("SELECT id,name,phone FROM clients ORDER BY name"):
                print(f"{row[0]} | {row[1]} | {row[2] or '-'}")
        elif args.cmd == "vendas":
            for row in connection.execute("SELECT s.id,c.name,s.description,s.amount,s.created_at,s.paid,s.due_date FROM sales s JOIN clients c ON c.id=s.client_id ORDER BY s.id DESC"):
                status = "PAGO" if row[5] else f"PENDENTE · vence {row[6] or '-'}"
                print(f"{row[0]} | {row[1]} | {row[2]} | R$ {row[3]:.2f} | {status} | {row[4]}")
        elif args.cmd == "pendentes":
            rows = connection.execute("SELECT s.id,c.name,s.description,s.amount,s.due_date FROM sales s JOIN clients c ON c.id=s.client_id WHERE s.paid=0 ORDER BY COALESCE(s.due_date,'9999-12-31'),s.id").fetchall()
            if not rows:
                print("Nenhuma venda pendente")
            for row in rows:
                atraso = " · ATRASADA" if row[4] and row[4] < date.today().isoformat() else ""
                print(f"{row[0]} | {row[1]} | {row[2]} | R$ {row[3]:.2f} | vence {row[4] or '-'}{atraso}")
        elif args.cmd == "receber":
            cursor = connection.execute("UPDATE sales SET paid=1,paid_at=CURRENT_TIMESTAMP WHERE id=? AND paid=0", (args.venda,))
            if cursor.rowcount == 0:
                parser.error("venda não encontrada ou já estava paga")
            connection.commit()
            print(f"Venda {args.venda} marcada como recebida")
        elif args.cmd == "exportar":
            print(f"{export_csv(connection, args.arquivo)} venda(s) exportada(s) para {args.arquivo}")
        else:
            count, total, received, pending = connection.execute("SELECT COUNT(*),COALESCE(SUM(amount),0),COALESCE(SUM(CASE WHEN paid=1 THEN amount ELSE 0 END),0),COALESCE(SUM(CASE WHEN paid=0 THEN amount ELSE 0 END),0) FROM sales").fetchone()
            clients = connection.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
            print(f"Clientes: {clients}\nVendas: {count}\nTotal vendido: R$ {total:.2f}\nRecebido: R$ {received:.2f}\nA receber: R$ {pending:.2f}")
    except sqlite3.IntegrityError as exc:
        parser.error(f"dados inválidos: {exc}")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
