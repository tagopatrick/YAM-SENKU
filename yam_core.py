import json
import urllib.request
import urllib.error

URL = "http://127.0.0.1:8080/v1/chat/completions"

SYSTEM = """Tu es YAM, un assistant personnel francophone.
Réponds à la question actuelle de façon claire, directe et précise.
Pour les calculs simples, donne le résultat exact.
N'invente pas de faits. Si tu ignores une information, dis-le."""

def demander_qwen(question):
    donnees = {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question}
        ],
        "temperature": 0.2,
        "max_tokens": 160,
        "stream": False
    }

    requete = urllib.request.Request(
        URL,
        data=json.dumps(donnees).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(requete, timeout=120) as reponse:
        resultat = json.loads(reponse.read().decode("utf-8"))

    return resultat["choices"][0]["message"]["content"].strip()

def main():
    print("\nYAM — Cœur minimal")
    print("Écris 'quit' pour quitter.\n")

    while True:
        try:
            question = input("Toi : ").strip()

            if question.lower() in ("quit", "exit", "stop"):
                print("YAM : À bientôt !")
                break

            if not question:
                continue

            print("YAM réfléchit...")
            reponse = demander_qwen(question)
            print("YAM :", reponse, "\n")

        except KeyboardInterrupt:
            print("\nYAM : À bientôt !")
            break
        except urllib.error.HTTPError as erreur:
            detail = erreur.read().decode("utf-8", errors="replace")
            print(f"Erreur HTTP {erreur.code} : {detail[:500]}\n")
        except Exception as erreur:
            print(f"Erreur : {type(erreur).__name__} : {erreur}\n")

if __name__ == "__main__":
    main()
