#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

python3 -m venv .venv-rpm
.venv-rpm/bin/python -m pip install --upgrade pip
.venv-rpm/bin/python -m pip install -r requirements_gui.txt pyinstaller
.venv-rpm/bin/pyinstaller --noconfirm --clean --onedir --windowed --name TakeoutLimpieza --collect-all tkinterdnd2 takeout_limpieza_fedora.py

TOP="$ROOT/packaging/fedora/rpmbuild"
mkdir -p "$TOP"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
rm -f "$TOP/SOURCES/takeout-limpieza-dist.tar.gz"
tar -C dist -czf "$TOP/SOURCES/takeout-limpieza-dist.tar.gz" TakeoutLimpieza
cp "$ROOT/packaging/fedora/takeout-limpieza.spec" "$TOP/SPECS/"
rpmbuild -bb --define "_topdir $TOP" "$TOP/SPECS/takeout-limpieza.spec"
echo "RPM generado en: $TOP/RPMS"
