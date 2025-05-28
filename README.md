# gemmit

**gemmit** ist ein Kommandozeilen-Tool, das mithilfe von Google Gemini KI automatisch prägnante und konforme Git-Commit-Messages generiert. Es analysiert die gestagten Änderungen im Repository, erstellt daraus einen Prompt und lässt von Gemini eine Commit-Message im [Conventional Commits](https://www.conventionalcommits.org/) Format verfassen.

## Features

- Automatische Generierung von Commit-Messages auf Deutsch (oder anderer Sprache)
- Berücksichtigt die letzten Commits, geänderte Dateien und den aktuellen Diff
- Nutzt Google Gemini API für hochwertige Commit-Botschaften
- Einfache Integration in bestehende Git-Workflows

## Voraussetzungen

- Python 3.10+
- [google-genai](https://pypi.org/project/google-genai/) Python-Paket (`pip install google-genai`)
- Ein API-Key für Google Gemini (siehe unten)

## Installation

1. Klone das Repository oder kopiere `gemmit.py` in dein Projektverzeichnis.
2. Installiere die benötigte Bibliothek:
   ```bash
   pip install google-genai
   ```
3. Lege deinen Gemini API-Key als Umgebungsvariable an:
   ```bash
   export GEMINI_API_KEY="dein-api-key"
   ```
   Oder speichere ihn in `~/.config/gemmit/key.txt`.

## Verwendung

1. Stage deine Änderungen wie gewohnt:
   ```bash
   git add <dateien>
   ```
2. Starte das Tool:
   ```bash
   python gemmit.py
   ```
   Optional kannst du die Sprache angeben (Standard: deutsch):
   ```bash
   python gemmit.py englisch
   ```
3. Die generierte Commit-Message wird angezeigt. Bestätige mit `gemmit`, um den Commit auszuführen.

## Hinweise

- Das Tool generiert Commit-Messages nur für gestagte Änderungen.
- Die Commit-Message entspricht dem Conventional Commits Standard.
- Die Kommunikation mit Gemini erfolgt über die Google API (es können Kosten entstehen).

## Lizenz

MIT License

