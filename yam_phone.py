import json, os, subprocess, datetime
AUTH_FILE=os.path.expanduser("~/YAM/autorisations.json")

def load_auth():
    if not os.path.exists(AUTH_FILE):
        base={"lire_sms":False,"repondre_sms":False,"acheter_unites":False,"acheter_megas":False,"actualites_auto":False}
        with open(AUTH_FILE,"w") as f: json.dump(base,f,indent=2)
        return base
    with open(AUTH_FILE,"r") as f: return json.load(f)

def cmd(c):
    try: return subprocess.getoutput(c)
    except: return ""

print("📱 YAM PHONE CONTROL - Ouaga")
auth=load_auth()
print(f"Autorisations: {auth}")

# 1. LIRE SMS (besoin termux-api app)
print("\n--- SMS ---")
if auth["lire_sms"]:
    sms=cmd("termux-sms-list -l 5 2>&1")
    print(sms[:500])
    print("\n💡 YAM suggère réponse: 'Salut, je te réponds plus tard, je suis en focus 50min'")
else:
    print("❌ Autorisation lire_sms = False. Pour activer: édite ~/YAM/autorisations.json")

# 2. BLOQUER APPELS (mode Ne pas déranger)
print("\n--- APPELS ---")
print("YAM peut mettre silencieux quand tu es en focus:")
print("termux-volume -s ringer 0  # coupe sonnerie")
print("termux-notification --content 'YAM: Mode focus - appels bloqués'")

# 3. ACHETER UNITES/MEGAS (avec ton autorisation)
if auth["acheter_unites"] or auth["acheter_megas"]:
    print("\n--- ACHAT (USSD) ---")
    # Exemple Orange BF - tu me diras ton opérateur
    # *144*...# pour Orange
    code=input("Code USSD à composer (ex *144*3*1# pour 1Go): ")
    confirm=input(f"Tu autorises YAM à composer {code} ? oui/non: ")
    if confirm.lower()=="oui":
        print(f"📞 Composition {code}...")
        # cmd(f"termux-telephony-call {code}")
        print("(Décommenté après ton test - sécurité)")
    else: print("❌ Annulé")
else:
    print("\n❌ Achat unités/mégas désactivé. Active dans autorisations.json")

# 4. ACTUALITES QUAND EN LIGNE
if auth["actualites_auto"]:
    print("\n--- ACTUS (quand online) ---")
    news=cmd("curl -s 'https://wttr.in/Ouagadougou?format=3' 2>&1")
    print(news)
