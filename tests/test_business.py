import tempfile
import unittest
from pathlib import Path

from business import connect, export_csv


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


if __name__ == "__main__":
    unittest.main()
