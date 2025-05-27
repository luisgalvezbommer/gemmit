import subprocess
import requests
import os

# Hole den Git-Diff der gestagten Änderungen
def get_git_diff():
    result = subprocess.run(['git', 'diff', '--cached'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

# Sende den Diff an die Gemini API
def generate_commit_message(diff, api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + api_key
    headers = {"Content-Type": "application/json"}
    prompt = f"Schreibe eine prägnante Commit-Message basierend auf folgendem git diff:\n{diff}"
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    message = response.json()['candidates'][0]['content']['parts'][0]['text']
    return message.strip()

# API-Key aus Umgebungsvariable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Setze die Umgebungsvariable GEMINI_API_KEY")

diff = get_git_diff()
if not diff:
    print("Keine gestagten Änderungen gefunden.")
    exit(0)

commit_message = generate_commit_message(diff, api_key)
print("\n🔧 Generierte Commit-Message:\n")
print(commit_message)

# Optional automatisch ausführen:
# subprocess.run(['git', 'commit', '-m', commit_message])
