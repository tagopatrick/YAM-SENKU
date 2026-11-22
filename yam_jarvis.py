import os, json, datetime
from pathlib import Path

MEM="jarvis_memory.json"
AUDIO_FILE=os.path.join(os.getcwd(), "yam_jarvis_voix.mp3")

def charger():
    if not Path(MEM).exists():
        return {"frere":"petit frere du milieu","souvenirs":[]}
    return json.loads(open(MEM,encoding="utf-8").read())

def sauver(m):
    open(MEM,"w",encoding="utf-8").write(json.dumps(m,indent=2,ensure_ascii=False))

def parler_humain(txt):
    print(f"\n🤖 YAM (voix humaine): {txt}\n")
    try:
        from gtts import gTTS
        print("🌐 Génération voix humaine Google...")
        gTTS(txt, lang='fr', slow=False).save(AUDIO_FILE)
        print(f"✅ Fichier créé: {AUDIO_FILE} ({Path(AUDIO_FILE).stat().st_size//1024}KB)")
        # mpv avec le bon chemin
        os.system(f'mpv --no-video --really-quiet {AUDIO_FILE}')
        print("🔊 Lecture terminée")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        os.system(f'espeak -v fr+m3 -s 130 "{txt}"')
        return False

m=charger()
now=datetime.datetime.now().strftime("%H:%M")

print("""
\033[96m╔════════════════════════════════════╗
║  YAM JARVIS - VOIX HUMAINE V3        ║
║  Fix: /tmp -> ~/YAM/                ║
╚════════════════════════════════════╝\033[0m
""")

ok = parler_humain(f"Patron, il est {now}. Enfin la belle voix humaine. Plus de robot. Je suis YAM, parti de Ouaga, objectif Espace.")
if ok:
    parler_humain("Test reussi. Ma memoire du petit frere du milieu est active. Je retiens tout pour toi.")

m["souvenirs"].append(f"{now} - Voix humaine OK")
sauver(m)
