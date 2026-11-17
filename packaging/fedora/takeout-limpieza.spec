Name:           takeout-limpieza
Version:        1.0.0
Release:        1%{?dist}
Summary:        Offline Google Takeout photo metadata sidecar cleaner
License:        LicenseRef-Unknown
BuildArch:      x86_64
Source0:        takeout-limpieza-dist.tar.gz

%description
Offline graphical utility that removes only Google Takeout JSON metadata sidecar
files associated with photos. Photo files are never modified or removed.

%prep
%setup -q -n TakeoutLimpieza

%build

%install
mkdir -p %{buildroot}/opt/takeout-limpieza
cp -a . %{buildroot}/opt/takeout-limpieza/
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/takeout-limpieza <<'EOF'
#!/bin/sh
exec /opt/takeout-limpieza/TakeoutLimpieza "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/takeout-limpieza
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/takeout-limpieza.desktop <<'EOF'
[Desktop Entry]
Name=Limpiador de Google Takeout
Comment=Quita JSON de metadatos asociados a fotos
Exec=takeout-limpieza
Terminal=false
Type=Application
Categories=Utility;FileTools;
EOF

%files
/opt/takeout-limpieza
%{_bindir}/takeout-limpieza
%{_datadir}/applications/takeout-limpieza.desktop

%changelog
* Tue Nov 17 2026 Codex <codex@users.noreply.github.com> - 1.0.0-1
- Initial package

