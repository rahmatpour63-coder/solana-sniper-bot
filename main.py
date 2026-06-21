name: Build Windows EXE

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          pip install -r requirements.txt

      - name: Build Windows EXE
        run: |
          pip install flet pyinstaller
          flet build windows --yes

      - name: Upload Windows EXE Artifact
        uses: actions/upload-artifact@v4
        with:
          name: windows-app
          path: build/windows
