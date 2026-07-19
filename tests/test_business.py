import tempfile
import unittest
from pathlib import Path

from business import connect, export_csv, main


class BusinessTests(unittest.TestCase):
    def test_schema_and_export(self):
        with tempfile.TemporaryDirectory() as directory:
            connection = connect(Path(directory) / "test.db")
            connection.execute("INSERT INTO clients(name) VALUES('Cliente Exemplo')")
            connection.execute("INSERT INTO sales(client_id,description,amount) VALUES(1,'Servico',10)")
            connection.commit()
            output = Path(directory) / "sales.csv"
            self.assertEqual(export_csv(connection, output), 1)
            self.assertIn("Cliente Exemplo", output.read_text(encoding="utf-8-sig"))
            connection.close()

    def test_foreign_key(self):
        with tempfile.TemporaryDirectory() as directory:
            connection = connect(Path(directory) / "test.db")
            with self.assertRaises(Exception):
                connection.execute("INSERT INTO sales(client_id,description,amount) VALUES(99,'X',1)")
            connection.close()

    def test_credit_sale_and_payment(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "test.db"
            self.assertEqual(main(["--db", str(db), "cliente", "Maria"]), 0)
            self.assertEqual(main(["--db", str(db), "venda", "1", "Uniforme", "120", "--vencimento", "2030-05-10"]), 0)
            connection = connect(db)
            self.assertEqual(connection.execute("SELECT paid,due_date FROM sales").fetchone(), (0, "2030-05-10"))
            connection.close()
            self.assertEqual(main(["--db", str(db), "receber", "1"]), 0)
            connection = connect(db)
            self.assertEqual(connection.execute("SELECT paid FROM sales").fetchone()[0], 1)
            connection.close()

    def test_migrates_existing_database(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "old.db"
            raw = __import__("sqlite3").connect(db)
            raw.execute("CREATE TABLE sales(id INTEGER PRIMARY KEY,client_id INTEGER,description TEXT,amount REAL,created_at TEXT)")
            raw.close()
            connection = connect(db)
            columns = {row[1] for row in connection.execute("PRAGMA table_info(sales)")}
            self.assertTrue({"paid", "due_date", "paid_at"}.issubset(columns))
            connection.close()


if __name__ == "__main__":
    unittest.main()
