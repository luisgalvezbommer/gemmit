import subprocess
import os
import sys
import tempfile
from google import genai


def run_command(cmd: list[str]) -> str:
    """Hilfsfunktion zum Ausführen von Git-Befehlen"""
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()

def build_prompt() -> str:
    """Erstellt einen ausführlichen Prompt für die Commit-Generierung."""

    language = sys.argv[1] if len(sys.argv) > 1 else "deutsch"
    
    # Letzte 3 Commits (Header + Body)
    recent_commits = run_command(["git", "log", "-3", "--pretty=format:%s%n%b%n---"])
    
    # Geänderte Dateien (staged)
    changed_files = run_command(["git", "diff", "--cached", "--name-only"])
    
    # Diff der Staging Area
    diff = run_command(["git", "diff", "--staged", "--cached"])
    
    # Prompt zusammenbauen
    prompt = f"""
# Kontextinformationen für die Commit-Generierung

## Die letzten Commits im Projekt:
{recent_commits}

## Es wurden folgende Dateien geändert:
{changed_files}

# Hier ist das Git-Diff der aktuellen Änderung:
{diff}

# Aufgabe 

Schreibe eine prägnante Commit-Message auf {language}.
Die Commit-Message soll dem Conventional Commits Standard entsprechen.
Gib den Commit so zurück, dass die erste Zeile den Commit-Header darstellt (z. B. feat: ...) 
und darunter (durch eine Leerzeile getrennt) ein optionaler Body folgt, der die Änderung bei Bedarf genauer beschreibt.
"""
    return prompt.strip()


# Hole den Git-Diff der gestagten Änderungen
def get_git_diff():
    result = subprocess.run(['git', 'diff', '--staged', '--cached'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

# Sende den Diff an die Gemini API
def generate_commit_message(diff, api_key):
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=build_prompt().encode('utf-8'),   
    )
    return response.text.strip()

def get_head_and_body(commit_message):
    # Trenne die Commit-Message in Head und Body
    lines = commit_message.split('\n')
    head = lines[0] if lines else ''
    body = '\n'.join(lines[1:]) if len(lines) > 1 else ''
    return head, body

def execute_commit(head, body):
    # Führe den Commit mit der generierten Nachricht aus
    if body:
        subprocess.run(['git', 'commit', '-m', head, '-m', body])
    else:
        subprocess.run(['git', 'commit', '-m', head])

def get_api_key():
    # 1. Versuch: Umgebungsvariable
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key

    # 2. Versuch: Datei ~/.config/gemmit/key.txt
    key_file = os.path.expanduser("~/.config/gemmit/key.txt")
    if os.path.exists(key_file):
        with open(key_file, "r", encoding="utf-8") as f:
            api_key = f.read().strip()
            if api_key:
                return api_key

    # Wenn beides fehlschlägt
    raise ValueError("API-Key nicht gefunden. Setze die Umgebungsvariable GEMINI_API_KEY oder speichere ihn in ~/.config/gemmit/key.txt")


# API-Key aus Umgebungsvariable
api_key = get_api_key()
if not api_key:
    raise ValueError("Setze die Umgebungsvariable GEMINI_API_KEY")

diff = get_git_diff()
if not diff:
    print("Keine gestagten Änderungen gefunden.")
    exit(0)

def edit_or_commit(commit_message):
    print("\n🔧 Generierte Commit-Message:\n")
    print(commit_message)
    head, body = get_head_and_body(commit_message)
    
    execute = input("\nCommit durchführen? Tippe 'gemmit'. Commit bearbeiten? Tippe 'edit': ")
    if execute.lower() == 'gemmit':
        execute_commit(head, body)
        print("\n✅ Commit erfolgreich ausgeführt.")
    elif execute.lower() == 'edit':
        # Temporäre Datei erstellen und Commit-Message hineinschreiben
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmpfile:
            tmpfile.write(commit_message)
            tmpfile.flush()
            tmp_path = tmpfile.name

        # vim mit der temporären Datei öffnen
        subprocess.run(['vim', tmp_path])

        # Datei erneut öffnen und bearbeitete Commit-Message einlesen
        with open(tmp_path, 'r') as file:
            edited_message = file.read().strip()

        # Erneute Anfrage ob commit oder edit
        edit_or_commit(edited_message)

        # Temporäre Datei löschen
        os.unlink(tmp_path)


def main():
    commit_message = generate_commit_message(diff, api_key)

    edit_or_commit(commit_message)

if __name__ == "__main__":
    main()
    
