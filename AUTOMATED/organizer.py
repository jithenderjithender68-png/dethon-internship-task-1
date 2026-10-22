import argparse
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


EXTENSION_CATEGORIES = {
    **{
        extension: "Documents"
        for extension in (
            ".doc", ".docx", ".odt", ".pdf", ".ppt", ".pptx", ".rtf",
            ".txt", ".xls", ".xlsx",
        )
    },
    **{
        extension: "Images"
        for extension in (
            ".bmp", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".tif",
            ".tiff", ".webp",
        )
    },
    **{
        extension: "Videos"
        for extension in (
            ".avi", ".flv", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg",
            ".mpg", ".webm", ".wmv",
        )
    },
    **{
        extension: "Archives"
        for extension in (
            ".7z", ".bz2", ".gz", ".rar", ".tar", ".xz", ".zip",
        )
    },
    **{
        extension: "Code"
        for extension in (
            ".c", ".cpp", ".cs", ".css", ".go", ".h", ".htm", ".html",
            ".java", ".js", ".json", ".php", ".py", ".rb", ".rs", ".sh",
            ".ts", ".xml", ".yaml", ".yml",
        )
    },
}


@dataclass
class OrganizeResult:
    moved: int = 0
    planned: int = 0
    unsupported: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)


def _available_destination(folder: Path, filename: str) -> Path:
    candidate = folder / filename
    if not os.path.lexists(candidate):
        return candidate

    source = Path(filename)
    index = 1
    while True:
        candidate = folder / f"{source.stem} ({index}){source.suffix}"
        if not os.path.lexists(candidate):
            return candidate
        index += 1


def organize_directory(directory: Path, dry_run: bool = False) -> OrganizeResult:
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    result = OrganizeResult()
    with os.scandir(directory) as entries:
        for entry in entries:
            try:
                if not entry.is_file(follow_symlinks=False):
                    continue
                category = EXTENSION_CATEGORIES.get(Path(entry.name).suffix.lower())
                if category is None:
                    result.unsupported += 1
                    continue

                destination_folder = directory / category
                if dry_run:
                    result.planned += 1
                    continue

                destination_folder.mkdir(exist_ok=True)
                while True:
                    destination = _available_destination(
                        destination_folder, entry.name
                    )
                    try:
                        shutil.move(entry.path, destination)
                        result.moved += 1
                        break
                    except FileExistsError:
                        continue
            except (FileExistsError, PermissionError, OSError) as error:
                result.failed += 1
                result.errors.append(f"{entry.name}: {error}")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sort files into category folders without overwriting existing files."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=Path.home() / "Downloads",
        help="directory to organize (default: ~/Downloads)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show how many files would be moved without changing anything",
    )
    arguments = parser.parse_args()

    try:
        result = organize_directory(arguments.directory, arguments.dry_run)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    for error in result.errors:
        print(f"Could not move {error}", file=sys.stderr)

    if arguments.dry_run:
        print(f"Files that would be relocated: {result.planned}")
    else:
        print(f"Files relocated: {result.moved}")
    print(f"Unsupported files left in place: {result.unsupported}")
    print(f"Files that could not be moved: {result.failed}")
    return 1 if result.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
