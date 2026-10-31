#!/usr/bin/env python3
"""
Install all imported libraries from a Jupyter notebook into .venv.

Usage:
    inst-imp.py <notebook-name>
    inst-imp.py note-03.ipynb
"""

import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VENV_PYTHON = SCRIPT_DIR.parent / ".venv" / "bin" / "python"


def extract_imports(notebook_path: Path) -> list[str]:
    """Parse a .ipynb file and return a list of top-level package names."""
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    imports: set[str] = set()

    for cell in nb.get("cells", []):
        source = cell.get("source", [])
        if isinstance(source, list):
            source = "".join(source)

        # import <package> [as ...]
        for m in re.finditer(
            r"^\s*import\s+([\w][\w.]*?)(?:\s|$|\s+#)", source, re.MULTILINE
        ):
            top = m.group(1).split(".")[0].strip()
            imports.add(top)

        # from <package> import ...
        for m in re.finditer(
            r"^\s*from\s+([\w][\w.]*?)\s+import", source, re.MULTILINE
        ):
            top = m.group(1).split(".")[0].strip()
            imports.add(top)

    # import name → PyPI package name
    pypi_map = {
        "sklearn": "scikit-learn",
        "cv2": "opencv-python",
        "PIL": "Pillow",
        "bs4": "beautifulsoup4",
        "yaml": "pyyaml",
        "gi": "PyGObject",
        "cairo": "pycairo",
    }

    # Remove common non-PyPI / stdlib packages
    stdlib = {
        "random",
        "os",
        "sys",
        "json",
        "re",
        "math",
        "collections",
        "itertools",
        "functools",
        "pathlib",
        "typing",
        "dataclasses",
        "logging",
        "time",
        "datetime",
        "copy",
        "abc",
        "contextlib",
        "enum",
        "pprint",
        "textwrap",
        "string",
        "io",
        "glob",
        "shutil",
        "subprocess",
        "argparse",
        "unittest",
        "traceback",
        "warnings",
        "inspect",
        "numbers",
        "decimal",
        "fractions",
        "statistics",
        "struct",
        "codecs",
        "unicodedata",
        "operator",
        "heapq",
        "bisect",
        "array",
        "weakref",
        "types",
        "pickle",
        "hashlib",
        "hmac",
        "secrets",
        "tempfile",
        "zipfile",
        "tarfile",
        "gzip",
        "bz2",
        "lzma",
        "zlib",
        "signal",
        "threading",
        "multiprocessing",
        "concurrent",
        "asyncio",
        "select",
        "socket",
        "ssl",
        "selectepoll",
        "selectors",
        "queue",
        "difflib",
        "csv",
        "configparser",
        "tomllib",
        "netrc",
        "platform",
        "errno",
        "ctypes",
        "posixpath",
        "ntpath",
        "genericpath",
        "fnmatch",
        "stat",
        "fileinput",
        "filecmp",
        "linecache",
        "site",
        "builtins",
        "__future__",
        "number",
        "base64",
        "binascii",
        "calender",
        "email",
        "html",
        "xml",
        "urllib",
        "http",
        "ftplib",
        "poplib",
        "imaplib",
        "smtplib",
        "uuid",
        "socketserver",
        "xmlrpc",
        "ipaddress",
        "mailbox",
        "mimetypes",
        "encodings",
        "pdb",
        "profile",
        "timeit",
        "dis",
        "compileall",
        "symtable",
        "token",
        "keyword",
        "ast",
        "zipimport",
        "pkgutil",
        "modulefinder",
        "importlib",
        "venv",
        "ensurepip",
        "distutils",
        "setuptools",
        "wheel",
        "pip",
    }

    result = []
    for imp in sorted(imports - stdlib):
        result.append(pypi_map.get(imp, imp))
    return result


def install(packages: list[str]) -> None:
    """Run pip install for all collected packages."""
    if not packages:
        print("No external packages to install.")
        return

    print(f"Installing {len(packages)} package(s):")
    for p in packages:
        print(f"  - {p}")
    print()

    result = subprocess.run(
        [str(VENV_PYTHON), "-m", "pip", "install", *packages],
        cwd=SCRIPT_DIR,
    )
    if result.returncode != 0:
        print(f"\n[ERROR] pip install failed with code {result.returncode}")
        sys.exit(1)

    print(f"\nDone. {len(packages)} package(s) installed.")


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <notebook-name>")
        print(f"Example: {sys.argv[0]} note-03.ipynb")
        sys.exit(1)

    notebook_name = sys.argv[1]
    notebook_path = SCRIPT_DIR / notebook_name

    if not notebook_path.exists():
        print(f"[ERROR] Notebook not found: {notebook_path}")
        sys.exit(1)

    packages = extract_imports(notebook_path)
    install(packages)


if __name__ == "__main__":
    main()
