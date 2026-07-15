import tempfile, unittest
from pathlib import Path
from business import connect
class TestDB(unittest.TestCase):
 def test_schema(self):
  with tempfile.TemporaryDirectory() as d:
   c=connect(Path(d)/"test.db"); names={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}; c.close(); self.assertIn("clients",names); self.assertIn("sales",names)
if __name__=="__main__": unittest.main()
