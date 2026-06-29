# ENV Known Issues

| Date | Issue | Workaround | Status |
|------|-------|-----------|--------|
| 2026-06-23 | PowerShell quoting breaks Python -c multi-line strings | Use script files or cmd.exe /c echo | Active |
| 2026-06-23 | Network to PyPI/GitHub unstable | Use SSH git, pip --no-deps, retry logic | Active |
| 2026-06-23 | node_modules on Windows causes path length issues | Keep under .gitignore, use npm ci | Active |
