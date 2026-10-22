import tempfile
import unittest
from pathlib import Path

from organizer import organize_directory


class OrganizeDirectoryTests(unittest.TestCase):
    def test_moves_supported_files_and_preserves_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "report.pdf").write_text("new")
            (root / "photo.JPG").write_text("image")
            (root / "notes.xyz").write_text("unsupported")
            documents = root / "Documents"
            documents.mkdir()
            (documents / "report.pdf").write_text("existing")

            result = organize_directory(root)

            self.assertEqual(result.moved, 2)
            self.assertEqual(result.unsupported, 1)
            self.assertEqual(result.failed, 0)
            self.assertEqual((documents / "report.pdf").read_text(), "existing")
            self.assertEqual((documents / "report (1).pdf").read_text(), "new")
            self.assertTrue((root / "Images" / "photo.JPG").is_file())
            self.assertTrue((root / "notes.xyz").is_file())

    def test_dry_run_does_not_change_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "report.pdf").write_text("document")

            result = organize_directory(root, dry_run=True)

            self.assertEqual(result.planned, 1)
            self.assertEqual(result.moved, 0)
            self.assertFalse((root / "Documents").exists())
            self.assertTrue((root / "report.pdf").is_file())

    def test_rejects_missing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_directory = Path(temporary_directory) / "missing"

            with self.assertRaises(ValueError):
                organize_directory(missing_directory)


if __name__ == "__main__":
    unittest.main()
