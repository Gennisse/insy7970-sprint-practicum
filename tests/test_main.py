from pathlib import Path
import tempfile
import unittest

from main import format_table, inspect_csv


class CsvInspectorTests(unittest.TestCase):
    def write_csv(self, content: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "sample.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def test_inspect_csv_counts_rows_and_lists_columns(self) -> None:
        csv_path = self.write_csv("name,age\nAlice,30\nBob,25\n")

        report = inspect_csv(csv_path, head=5)

        self.assertIn("Row count: 2", report)
        self.assertIn("Column names: name, age", report)
        self.assertIn("Alice", report)
        self.assertIn("Bob", report)

    def test_inspect_csv_handles_short_preview(self) -> None:
        csv_path = self.write_csv("name,age\nAlice,30\n")

        report = inspect_csv(csv_path, head=5)

        self.assertIn("Requested 5 rows, but only 1 were available.", report)

    def test_format_table_keeps_commas_inside_fields_readable(self) -> None:
        table = format_table(["note", "value"], [["quoted, text", "7"]])

        self.assertIn("quoted, text", table)


if __name__ == "__main__":
    unittest.main()
