"""Utility to clean project workspace for faster startup and smaller size.

Usage:
    python clean.py

It will remove __pycache__ directories, delete temporary export files, and optionally rebuild virtual environment.
"""
import os
import shutil

ROOT = os.path.dirname(__file__)

def remove_pycache(path):
    for dirpath, dirnames, filenames in os.walk(path):
        if dirpath.endswith("__pycache__"):
            try:
                shutil.rmtree(dirpath)
                print(f"Removed {dirpath}")
            except Exception as e:
                print(f"Failed to remove {dirpath}: {e}")

if __name__ == "__main__":
    print("Cleaning project...\n")
    remove_pycache(ROOT)
    export_dir = os.path.join(ROOT, "export")
    if os.path.isdir(export_dir):
        for fname in os.listdir(export_dir):
            fpath = os.path.join(export_dir, fname)
            try:
                if os.path.isfile(fpath):
                    os.remove(fpath)
                    print(f"Deleted {fpath}")
            except Exception:
                pass
    print("Done.")