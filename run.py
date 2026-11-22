import os, random, datetime
from gtts import gTTS

pubs=[
"Parti de Ouaga, objectif Espace.",
"Aujourd'hui tu codes dans le bruit, demain on ecoutera ton histoire.",
"Travaille en silence, ta fusee fera le bruit au decollage.",
"YAM MODE : On ne recule pas, on ajuste la trajectoire."
]

p=random.choice(pubs)
d=datetime.datetime.now().strftime("%d/%m %H:%M")

print(f"\n--- PUB DU {d} ---")
print(p)
print("\n#YAM #Ouaga #Espace\n")

open("historique_pubs.txt","a", encoding="utf-8").write(f"{d} | {p}\n")

# Voix humaine
print("🔊 YAM parle...")
gTTS(p, lang='fr').save('yam.mp3')
os.system('mpv --no-video yam.mp3 2>/dev/null')
print("✅ Termine. Historique sauvegarde.")
