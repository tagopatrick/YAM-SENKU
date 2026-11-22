import os
import json
import subprocess
import datetime
import shutil
import urllib.request
from pathlib import Path
from urllib.parse import quote_plus, urljoin, unquote
from html.parser import HTMLParser

ROOT = Path.home() / "YAM"
MODEL = ROOT / "models/qwen2-0_5b-instruct-q4_k_m.gguf"
MEM_FILE = ROOT / "memoire/memoire.json"
CHARTE_FILE = ROOT / "CHARTE_YAM.md"

WIKI_URL = "http://127.0.0.1:8081/"
MAX_TOKENS = 256
MAX_HISTORIQUE = 5


# ================= MÉMOIRE =================

def charger_json():
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def sauvegarder_json(data):
    MEM_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MEM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def construire_memoire(memoire):
    faits = [
        "Nom de l'assistant : YAM",
        "Nom du créateur : son développeur",
    ]
    conversations = []

    for cle, valeur in memoire.items():
        if not isinstance(valeur, dict):
            continue

        if "question" in valeur:
            conversations.append((cle, valeur))
        elif "valeur" in valeur:
            faits.append(f"{cle} : {valeur['valeur']}")

    conversations.sort(
        key=lambda element: element[1].get("date", "")
    )

    recentes = conversations[-5:]
    historique = []

    for _, echange in recentes:
        historique.append(
            "Utilisateur : " + str(echange.get("question", "")) +
            "\\nYAM : " + str(echange.get("reponse", ""))
        )

    return (
        "FAITS À RETENIR :\\n" + "\\n".join(faits) +
        "\\n\\nCONVERSATIONS RÉCENTES :\\n" +
        "\\n\\n".join(historique)
    )

def charger_charte():
    try:
        return CHARTE_FILE.read_text(encoding="utf-8")
    except OSError:
        return "Sois honnête, respectueux, sympathique et efficace."


# ================= OUTILS =================

def commande_existe(nom):
    return shutil.which(nom) is not None


def parler(texte):
    print("\n🗣️ YAM :", texte)

    if commande_existe("termux-tts-speak"):
        try:
            subprocess.run(
                ["termux-tts-speak", texte[:1500]],
                timeout=60
            )
        except Exception as erreur:
            print("Voix indisponible :", erreur)


# ================= QWEN =================

def verifier_moteur():
    if not MODEL.is_file():
        raise FileNotFoundError(f"Modèle absent : {MODEL}")

    if not commande_existe("llama-cli"):
        raise RuntimeError("llama-cli introuvable.")

    print("✅ Qwen 0.5B détecté.")


def demander_qwen(systeme, question):
    prompt = (
        "<|im_start|>system\\n" + systeme + "<|im_end|>\\n"
        "<|im_start|>user\\n" + question + "<|im_end|>\\n"
        "<|im_start|>assistant\\n"
    )

    resultat = subprocess.run(
        [
            "llama-cli",
            "-m", str(MODEL),
            "-c", "1536",
            "-t", "2",
            "-n", str(MAX_TOKENS),
            "--no-display-prompt",
            "--simple-io",
            "--log-disable",
            "-p", prompt
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=90
    )

    if resultat.returncode != 0:
        raise RuntimeError(resultat.stderr[-1000:])

    sortie = resultat.stdout

    debut_reponse = sortie.rfind("<|im_start|>assistant")
    if debut_reponse != -1:
        sortie = sortie[debut_reponse + len("<|im_start|>assistant"):]

    reponse = sortie.strip()

    for marqueur in ("<|im_end|>", "<|im_start|>"):
        if marqueur in reponse:
            reponse = reponse.split(marqueur)[0]

    return reponse.strip()


# ================= WIKIPÉDIA =================

class ExtracteurLiens(HTMLParser):
    def __init__(self):
        super().__init__()
        self.liens = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href.startswith("/content/"):
                self.liens.append(href)


class ExtracteurTexte(HTMLParser):
    def __init__(self):
        super().__init__()
        self.contenu = []
        self.ignore = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.ignore += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self.ignore = max(0, self.ignore - 1)

    def handle_data(self, data):
        if not self.ignore:
            texte = " ".join(data.split())
            if texte:
                self.contenu.append(texte)


def lire_url(url):
    requete = urllib.request.Request(
        url, headers={"User-Agent": "YAM-Offline/1.0"}
    )
    with urllib.request.urlopen(requete, timeout=15) as reponse:
        return reponse.read().decode("utf-8", errors="replace")


def rechercher_wikipedia(sujet):
    try:
        url = WIKI_URL + "search?pattern=" + quote_plus(sujet)
        html = lire_url(url)

        liens = ExtracteurLiens()
        liens.feed(html)

        if not liens.liens:
            return ""

        articles = []

        for lien in liens.liens[:3]:
            page_url = urljoin(WIKI_URL, lien)
            page_html = lire_url(page_url)

            texte = ExtracteurTexte()
            texte.feed(page_html)

            titre = unquote(lien.split("/")[-1]).replace("_", " ")

            articles.append(
                "ARTICLE : " + titre + "\n" +
                "CONTENU : " + " ".join(texte.contenu)[:2500]
            )

        return "\n\n".join(articles)

    except Exception as erreur:
        print("Wikipédia indisponible :", erreur)
        return ""


# ================= PERSONNALITÉ =================

SYSTEM = f"""
Tu es YAM, un assistant numérique francophone.

PERSONNALITÉ :
- Chaleureux, naturel, poli et intelligent.
- Direct, clair et précis.
- Sérieux lorsque le sujet l'exige.
- Tu ne prétends pas avoir des émotions humaines.
- Tu reconnais honnêtement tes limites.

RÈGLES DE CONVERSATION :
- Tiens compte des informations mémorisées.
- Utilise les conversations précédentes lorsqu'elles sont pertinentes.
- Ne demande pas à l'utilisateur de répéter une information déjà présente.
- Réponds avec des phrases complètes.
- Termine tes phrases et évite les réponses coupées.
- Ne répète pas inutilement les mêmes informations.
- N'invente jamais de faits.

CHARTE DU DÉVELOPPEUR :
{charger_charte()}
"""


# ================= DÉMARRAGE =================

print("\n🧠 DÉMARRAGE DE YAM")

try:
    verifier_moteur()
except Exception as erreur:
    print("❌ Erreur moteur :", erreur)
    raise SystemExit(1)

print("🧠 Qwen connecté.")
print("💾 Mémoire persistante activée.")
print("📚 Wikipédia locale : port 8081")

parler("Salut ! YAM est prêt. Comment puis-je t'aider ?")


# ================= CONVERSATION =================

while True:
    try:
        question = input("\n👤 Toi : ").strip()

        if question.lower() in ("quit", "exit", "q", "stop"):
            break

        if not question:
            continue

        memoire = charger_json()

        if question.lower() == "memoire":
            print("\n💾 MÉMOIRE DE YAM")
            print(construire_memoire(memoire))
            continue

        contexte = construire_memoire(memoire)

        if question.lower().startswith("wiki "):
            sujet = question[5:].strip()
            print("📚 Recherche dans Wikipédia...")

            extraits = rechercher_wikipedia(sujet)

            if not extraits:
                parler("Je n'ai pas trouvé de contenu dans Wikipédia.")
                continue

            question_qwen = (
                contexte +
                "\n\nEXTRAITS DE WIKIPÉDIA :\n" + extraits +
                "\n\nQuestion : " + sujet
            )
        else:
            question_qwen = (
                contexte +
                "\n\nNOUVEAU MESSAGE DE L'UTILISATEUR :\n" +
                question
            )

        print("🧠 YAM réfléchit...")

        try:
            reponse = demander_qwen(SYSTEM, question_qwen)

            if not reponse:
                reponse = "Je n'ai pas réussi à formuler une réponse."

        except Exception as erreur:
            print("Erreur Qwen :", erreur)
            reponse = "Une erreur est survenue pendant ma réflexion."

        parler(reponse)

        identifiant = datetime.datetime.now().strftime(
            "chat_%Y%m%d_%H%M%S_%f"
        )

        memoire[identifiant] = {
            "question": question,
            "reponse": reponse,
            "date": datetime.datetime.now().isoformat()
        }

        sauvegarder_json(memoire)
        print("💾 Conversation sauvegardée.")

    except KeyboardInterrupt:
        break

    except Exception as erreur:
        print("Erreur :", erreur)

parler("À bientôt !")
print("YAM arrêté.")
