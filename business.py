"""Gestão local simples de clientes e vendas para pequenos negócios."""
import argparse, sqlite3
from pathlib import Path
DB=Path.home()/".agentos_business.db"
def connect(path=DB):
 c=sqlite3.connect(path); c.execute("CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY,name TEXT NOT NULL,phone TEXT DEFAULT '')"); c.execute("CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY,client_id INTEGER,description TEXT,amount REAL,created_at TEXT DEFAULT CURRENT_TIMESTAMP)"); return c
def main(argv=None):
 p=argparse.ArgumentParser(description="AgentOS Business Toolkit"); p.add_argument("--db",default=str(DB)); s=p.add_subparsers(dest="cmd",required=True)
 a=s.add_parser("cliente"); a.add_argument("nome"); a.add_argument("--telefone",default="")
 v=s.add_parser("venda"); v.add_argument("cliente",type=int); v.add_argument("descricao"); v.add_argument("valor",type=float)
 s.add_parser("resumo"); args=p.parse_args(argv); c=connect(args.db)
 if args.cmd=="cliente": c.execute("INSERT INTO clients(name,phone) VALUES(?,?)",(args.nome,args.telefone)); c.commit(); print("Cliente cadastrado")
 elif args.cmd=="venda": c.execute("INSERT INTO sales(client_id,description,amount) VALUES(?,?,?)",(args.cliente,args.descricao,args.valor)); c.commit(); print("Venda cadastrada")
 else:
  count,total=c.execute("SELECT COUNT(*),COALESCE(SUM(amount),0) FROM sales").fetchone(); print(f"Vendas: {count}\nTotal: R$ {total:.2f}")
if __name__=="__main__": main()
