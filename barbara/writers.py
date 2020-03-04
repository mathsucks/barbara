import os
import shutil
from pathlib import Path
from typing import Dict


class Writer:
    """Writes new environment to target file, preserving the original in a backup during the write."""

    def __init__(self, target_file: Path, environment: Dict[str, str]):
        self.target_file = target_file
        self.environment = environment

    def write(self):
        backup_file = Path(f"{self.target_file}.backup")
        shutil.copy2(self.target_file, backup_file)

        with self.target_file.open("w", encoding="utf-8") as f:
            f.seek(0)
            for k, v in self.environment.items():
                # Normalize falsy values to blanks
                v = "" if not v else v
                f.write(f"{k}={v}\n")

        os.remove(backup_file)
