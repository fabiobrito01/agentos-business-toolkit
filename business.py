"""Gestão local simples de clientes e vendas para pequenos negócios."""
import argparse
import csv
import sqlite3
from pathlib import Path

DB = Path.home() / ".agentos_business.db"


def connect(path=DB):
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY,name TEXT NOT NULL,phone TEXT DEFAULT '')")
    connection.execute("CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY,client_id INTEGER NOT NULL,description TEXT NOT NULL,amount REAL NOT NULL CHECK(amount >= 0),created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(client_id) REFERENCES clients(id))")
    return connection


def export_csv(connection, path):
    rows = connection.execute("SELECT s.id,c.name,s.description,s.amount,s.created_at FROM sales s JOIN clients c ON c.id=s.client_id ORDER BY s.id").fetchall()
    with open(path, "w", newline="", encoding="utf-8-sig") as output:
        writer = csv.writer(output)
        writer.writerow(("id", "cliente", "descricao", "valor", "data"))
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
    commands.add_parser("clientes")
    commands.add_parser("vendas")
    commands.add_parser("resumo")
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
            connection.execute("INSERT INTO sales(client_id,description,amount) VALUES(?,?,?)", (args.cliente, args.descricao, args.valor))
            connection.commit()
            print("Venda cadastrada")
        elif args.cmd == "clientes":
            for row in connection.execute("SELECT id,name,phone FROM clients ORDER BY name"):
                print(f"{row[0]} | {row[1]} | {row[2] or '-'}")
        elif args.cmd == "vendas":
            for row in connection.execute("SELECT s.id,c.name,s.description,s.amount,s.created_at FROM sales s JOIN clients c ON c.id=s.client_id ORDER BY s.id DESC"):
                print(f"{row[0]} | {row[1]} | {row[2]} | R$ {row[3]:.2f} | {row[4]}")
        elif args.cmd == "exportar":
            print(f"{export_csv(connection, args.arquivo)} venda(s) exportada(s) para {args.arquivo}")
        else:
            count, total = connection.execute("SELECT COUNT(*),COALESCE(SUM(amount),0) FROM sales").fetchone()
            clients = connection.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
            print(f"Clientes: {clients}\nVendas: {count}\nTotal: R$ {total:.2f}")
    except sqlite3.IntegrityError as exc:
        parser.error(f"dados inválidos: {exc}")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
