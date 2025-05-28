import subprocess
import os
from google import genai


# Hole den Git-Diff der gestagten Änderungen
def get_git_diff():
    result = subprocess.run(['git', 'diff', '--cached'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

# Sende den Diff an die Gemini API
def generate_commit_message(diff, api_key):
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt    
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

# API-Key aus Umgebungsvariable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Setze die Umgebungsvariable GEMINI_API_KEY")

diff = get_git_diff()
if not diff:
    print("Keine gestagten Änderungen gefunden.")
    exit(0)

prompt = f"""
Schreibe eine prägnante Commit-Message basierend auf folgendem Git-Diff:
{diff}
Die Commit-Message soll dem Conventional Commits Standard entsprechen.
Gib den Commit so zurück, dass die erste Zeile den Commit-Header darstellt (z. B. feat: ...) 
und darunter (durch eine Leerzeile getrennt) ein optionaler Body folgt, der die Änderung bei Bedarf genauer beschreibt.
"""


def main():
    commit_message = generate_commit_message(diff, api_key)
    print("\n🔧 Generierte Commit-Message:\n")
    print(commit_message)

    head, body = get_head_and_body(commit_message)
    # print("\nCommit Head:", head)
    # print("Commit Body:", body)
    
    execute = input("\nCommit durchführen? Tippe 'gemmit': ")
    if execute.lower() == 'gemmit':
        execute_commit(head, body)
        print("\n✅ Commit erfolgreich ausgeführt.")

if __name__ == "__main__":
    main()
    
