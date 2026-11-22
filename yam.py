import requests, re, html, json, os, subprocess, random, time, datetime
KIWIX="http://127.0.0.1:9060"
LLM="http://127.0.0.1:8080/v1/chat/completions"
ZIM_GLOB="/storage/emulated/0/Android/media/org.kiwix.kiwixmobile/Kiwix/*.zim /storage/emulated/0/Android/media/org.kiwix.kiwixmobile/*.zim"

# Couleurs néon
CYAN='\033[1;36m'
MAGENTA='\033[1;35m'
VERT='\033[1;32m'
JAUNE='\033[1;33m'
GRIS='\033[0;90m'
RESET='\033[0m'

# --- OUVERTURE DES APPLIS - intégrée, comme dans "ouvre" avec rish ---
def ouvrir_appli(nom):
    nom = nom.lower().strip()
    if nom.startswith("ouvre "):
        nom = nom[6:].strip()
    surnoms = {"yt": "youtube", "wa": "whatsapp", "insta": "instagram", "fb": "facebook", "tiktok lite": "musically", "tiktok": "musically", "capcut": "lvoverseas", "cap cut": "lvoverseas", "whatsapp business": "w4b", "tg": "telegram", "tele": "telegram"}
    cle = surnoms.get(nom, nom)
    fixes = {"whatsapp":"com.whatsapp","youtube":"com.google.android.youtube","instagram":"com.instagram.android","tiktok":"com.zhiliaoapp.musically","facebook":"com.facebook.katana","messenger":"com.facebook.orca","chrome":"com.android.chrome","kiwix":"org.kiwix.kiwixmobile","wikipedia":"org.wikipedia","telegram":"org.telegram.messenger.web","capcut":"com.lemon.lvoverseas"}
    if cle in fixes:
        pkg = fixes[cle]
        print(f"📱 J ouvre {nom} : {pkg}")
        # Comme ton "ouvre" : on trouve l'activité avec rish puis on lance
        try:
            os.system(f'rish -c "am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000 -p {pkg}" > /dev/null 2>&1')
        except:
            os.system(f'rish -c "am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000 -p {pkg}" > /dev/null 2>&1')
        return True
    try:
        out = subprocess.run(["rish","-c","cmd package list packages"], capture_output=True, text=True, timeout=10).stdout.lower()
        pkgs = [l.replace("package:","").strip() for l in out.splitlines() if "package:" in l]
        print(f"📱 Je vois {len(pkgs)} applis")
        mots = cle.split()
        for pkg in pkgs:
            if cle == "youtube" and "music" in pkg: continue
            if any(m in pkg for m in mots if len(m)>2):
                print(f"📱 J ouvre {nom} : {pkg}")
                os.system(f'rish -c "am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000 -p {pkg}" > /dev/null 2>&1')
                return True
        print(f"❌ Pas trouve {nom} dans les {len(pkgs)} applis")
    except Exception as e:
        print(f"Erreur cmd: {e}")
    return False

APPLIS_CONNUES = ["whatsapp","youtube","instagram","tiktok","facebook","messenger","chrome","kiwix","wikipedia","capcut","telegram","yt","wa","insta","fb"]

def dire_heure():
    now = datetime.datetime.now()
    return f"Il est {now.hour} heure {now.minute}"

def dire_meteo():
    try:
        r = requests.get("https://wttr.in/Ouagadougou?format=%t+%C", timeout=5)
        return f"A Ouaga, il fait {r.text.strip()}"
    except:
        return "Pas de connexion, mais a Ouaga il fait chaud comme d'hab"

def dire_date():
    now = datetime.datetime.now()
    jours = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
    mois = ["","janvier","fevrier","mars","avril","mai","juin","juillet","aout","septembre","octobre","novembre","decembre"]
    return f"On est {jours[now.weekday()]} {now.day} {mois[now.month]} {now.year}"

def calculer(expr):
    # On nettoie : on garde que chiffres et + - * / ( ) .
    expr = expr.lower().replace("calcule","").replace("calcul","").replace("combien fait","").replace("=","").strip()
    expr = expr.replace("x","*").replace("fois","*").replace("divise par","/").replace(",",".")
    # Securite : que des chiffres et operateurs
    autorise = "0123456789+-*/(). "
    if any(c not in autorise for c in expr) or not expr:
        return "Je n'ai pas compris le calcul. Essaie : calcule 25 * 4"
    try:
        res = eval(expr, {"__builtins__": {}}, {})
        return f"{expr} = {res}"
    except:
        return "Ce calcul ne marche pas, essaie autrement"

def lancer_minuteur(secondes, message="C'est l'heure !"):
    def sonne():
        print(f"\n⏰ ⏰ MINUTEUR : {message}")
        try:
            import subprocess as sp
            sp.run(["termux-tts-speak", message])
        except:
            pass
    import threading
    threading.Timer(secondes, sonne).start()
    if secondes >= 60:
        return f"Ok, minuteur lance pour {int(secondes//60)} minute(s). Je te previens."
    else:
        return f"Ok, minuteur lance pour {int(secondes)} seconde(s). Je te previens."



def gadget_batterie():
    try:
        import subprocess as sp, json as _js, os as _os
        # On essaie avec le chemin complet, c'est ca qui bloquait
        cmd = "/data/data/com.termux/files/usr/bin/termux-battery-status"
        if not _os.path.exists(cmd):
            cmd = "termux-battery-status"
        out = sp.run([cmd], capture_output=True, text=True, timeout=5).stdout
        print(f"DEBUG batterie raw: {out[:100]}")
        d = _js.loads(out)
        pct = d.get("percentage", "?")
        status = d.get("status", "")
        temp = d.get("temperature", "")
        return f"Ta batterie est a {pct}%, en {status}, {temp} degres."
    except Exception as e:
        return f"Erreur batterie : {e}"

def gadget_heure_pays(ville):
    import datetime as _dt
    villes = {"paris": ("Europe/Paris", "Paris"), "new york": ("America/New_York", "New York"), "newyork": ("America/New_York", "New York"), "londres": ("Europe/London", "Londres"), "dakar": ("Africa/Dakar", "Dakar"), "abidjan": ("Africa/Abidjan", "Abidjan"), "tokyo": ("Asia/Tokyo", "Tokyo"), "dubai": ("Asia/Dubai", "Dubai")}
    cle = ville.lower().strip()
    if cle not in villes:
        return f"Je ne connais pas {ville}. Essaie : Paris, Londres, Dakar, New York, Tokyo, Dubai"
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(villes[cle][0])
        now = _dt.datetime.now(tz)
        return f"A {villes[cle][1]}, il est {now.hour}h{now.minute:02d}"
    except:
        return "Je n'arrive pas a calculer l'heure la-bas."

def gadget_compte_rebours(n):
    import time as _t
    return n

def gadget_boule_magique():
    import random as _r
    reponses = ["Oui, c'est sur !", "Oui, sans aucun doute.", "Ca a l'air tres bien !", "Peut-etre, essaie encore.", "Je ne suis pas sur, reessaie.", "Non, pas vraiment.", "Non, oublie ca.", "C'est possible, mais pas sur.", "Fonce, c'est le moment !", "Mieux vaut attendre un peu."]
    return _r.choice(reponses)

def gadget_mot_de_passe():
    import random as _r, string as _s
    lettres = _s.ascii_letters + _s.digits + "!@#$"
    mdp = "".join(_r.choice(lettres) for _ in range(12))
    return f"Ton nouveau mot de passe fort : {mdp} . Note-le bien, ne le donne a personne."

def gadget_pseudo():
    import random as _r
    debut = ["Dark", "Super", "Mega", "King", "Queen", "Shadow", "Turbo", "Genius", "YAM", "Senku", "Ghost", "Fire"]
    fin = ["Boy", "Girl", "Genius", "Pro", "Master", "X", "2000", "BF", "Ouaga", "Star", "Legend"]
    return f"Ton nouveau pseudo : {_r.choice(debut)}{_r.choice(fin)}{_r.randint(10,99)}"

def gadget_age(annee):
    import datetime as _dt
    try:
        a = int(annee)
        age = _dt.datetime.now().year - a
        return f"Si tu es ne en {a}, tu as {age} ans, ou tu vas avoir {age} ans cette annee."
    except:
        return "Dis-moi ton annee, comme : je suis ne en 2005"

def gadget_quiz():
    import random as _r
    questions = [
        ("Quelle est la capitale du Burkina Faso ?", "ouagadougou"),
        ("Combien font 7 x 8 ?", "56"),
        ("Quel est le plus grand ocean ?", "pacifique"),
        ("Qui a ecrit Le Petit Prince ?", "saint-exupery"),
        ("Combien de jours dans une annee bissextile ?", "366"),
    ]
    q, r = _r.choice(questions)
    return q, r

def gadget_chanson():
    import random as _r
    chansons = [
        ("Je suis tombe du ciel, je suis une etoile...", "C'est une chanson de ... tu as trouve ? C'etait une devinette, dis 'autre chanson' pour une autre."),
        ("Ouaga, Ouaga, ma ville que j'aime tant...", "C'est une chanson d'amour pour Ouaga, tu as trouve ?"),
    ]
    return _r.choice(chansons)

def gadget_meteo(ville):
    try:
        import urllib.request as _ur, json as _js, urllib.parse as _up
        ville_clean = ville.strip() or "Ouagadougou"
        url = f"https://wttr.in/{_up.quote(ville_clean)}?format=j1"
        req = _ur.Request(url, headers={"User-Agent": "curl"})
        data = _js.loads(_ur.urlopen(req, timeout=8).read().decode())
        cur = data["current_condition"][0]
        temp = cur["temp_C"]
        ressenti = cur["FeelsLikeC"]
        desc = cur["weatherDesc"][0]["value"]
        humid = cur["humidity"]
        vent = cur["windspeedKmph"]
        return f"A {ville_clean}, il fait {temp} degres, ressenti {ressenti} degres, ciel : {desc}. Humidite {humid}%, vent {vent} km/h."
    except Exception as e:
        return f"Je n'arrive pas a avoir la meteo pour {ville}. Verifie ta connexion. Erreur : {e}"

def gadget_actu():
    try:
        import urllib.request as _ur, json as _js
        # On utilise une API gratuite sans cle
        url = "https://api.rss2json.com/v1/api.json?rss_url=https://www.francetvinfo.fr/titres.rss"
        data = _js.loads(_ur.urlopen(_ur.Request(url, headers={"User-Agent":"Mozilla"}), timeout=8).read().decode())
        items = data.get("items", [])[:3]
        if not items:
            return "Je n'ai pas trouve de nouvelles pour l'instant."
        txt = "Voici les 3 grosses nouvelles : "
        for i, it in enumerate(items, 1):
            txt += f"{i}. {it['title']}. "
        return txt
    except Exception as e:
        return f"Je n'arrive pas a avoir les nouvelles. Verifie ta connexion. Erreur : {e}"

def gadget_traduction(texte, langue):
    try:
        import urllib.request as _ur, urllib.parse as _up, json as _js
        # Dictionnaire simple pour les mots courants, + API gratuite
        dico = {
            "bonjour": {"anglais": "hello", "espagnol": "hola", "allemand": "hallo"},
            "merci": {"anglais": "thank you", "espagnol": "gracias", "allemand": "danke"},
            "au revoir": {"anglais": "goodbye", "espagnol": "adios", "allemand": "tschuss"},
            "comment ca va": {"anglais": "how are you", "espagnol": "como estas", "allemand": "wie geht es dir"},
            "je t'aime": {"anglais": "I love you", "espagnol": "te quiero", "allemand": "ich liebe dich"},
        }
        t = texte.lower().strip()
        lang = langue.lower().strip()
        if t in dico and lang in dico[t]:
            return f"'{texte}' en {langue} = {dico[t][lang]}"
        # Sinon API MyMemory gratuite
        lang_code = {"anglais": "en", "francais": "fr", "espagnol": "es", "allemand": "de", "arabe": "ar", "moore": "fr"}.get(lang, "en")
        url = f"https://api.mymemory.translated.net/get?q={_up.quote(texte)}&langpair=fr|{lang_code}"
        data = _js.loads(_ur.urlopen(url, timeout=8).read().decode())
        trad = data["responseData"]["translatedText"]
        return f"'{texte}' en {langue} = {trad}"
    except Exception as e:
        return f"Je n'arrive pas a traduire. Erreur : {e}"

def gadget_convertisseur(montant, de, vers):
    try:
        import urllib.request as _ur, json as _js
        # Taux fixes si pas de connexion, + API gratuite
        taux = {"fcfa": 1, "euro": 655.96, "euros": 655.96, "dollar": 600, "dollars": 600}
        de_l = de.lower()
        vers_l = vers.lower()
        # On passe par FCFA comme base
        if de_l in taux and vers_l in taux:
            en_fcfa = montant * taux[de_l] if de_l != "fcfa" else montant
            if vers_l == "fcfa":
                res = en_fcfa
            else:
                res = en_fcfa / taux[vers_l]
            return f"{montant} {de} = {res:.2f} {vers}"
        return "Je connais FCFA, euros et dollars pour l'instant."
    except Exception as e:
        return f"Erreur conversion : {e}"

def gadget_recherche(sujet):
    try:
        import urllib.request as _ur, urllib.parse as _up, json as _js
        sujet_clean = sujet.strip()
        # API Wikipedia en francais
        url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{_up.quote(sujet_clean)}"
        req = _ur.Request(url, headers={"User-Agent": "YAM-SENKU/1.0"})
        data = _js.loads(_ur.urlopen(req, timeout=10).read().decode())
        if "extract" in data:
            resume = data["extract"][:500]
            return f"Voila ce que j'ai trouve sur {sujet_clean} : {resume}"
        else:
            return f"Je n'ai rien trouve sur {sujet_clean} sur Wikipedia en francais."
    except Exception as e:
        return f"Je n'arrive pas a chercher '{sujet}'. Verifie ta connexion. Erreur : {e}"

import json as _json_mem, os as _os_mem
FICHIER_MEMOIRE = "yam_memoire.json"
def charger_memoire():
    try:
        if _os_mem.path.exists(FICHIER_MEMOIRE):
            return _json_mem.load(open(FICHIER_MEMOIRE, encoding="utf-8"))
    except:
        pass
    return {"listes": [], "notes": [], "agenda": [], "contacts": {"maman": "70000000", "papa": "70000000"}, "reveils": [], "dictees": [], "score_quiz": 0, "conversation": [], "prenom": "", "nom": ""}

def sauver_memoire(mem):
    try:
        open(FICHIER_MEMOIRE, "w", encoding="utf-8").write(_json_mem.dumps(mem, ensure_ascii=False, indent=2))
        return True
    except Exception as e:
        print(f"Erreur memoire: {e}")
        return False

MEMOIRE = charger_memoire()

def retenir_conversation(question, reponse=""):
    try:
        import datetime as _dt
        entree = {"date": _dt.datetime.now().strftime("%d/%m %H:%M"), "user": question, "yam": reponse}
        MEMOIRE.setdefault("conversation", []).append(entree)
        # On garde les 100 dernieres pour ne pas faire grossir le fichier
        MEMOIRE["conversation"] = MEMOIRE["conversation"][-100:]
        sauver_memoire(MEMOIRE)
    except:
        pass

def souvenir_recent(n=5):
    conv = MEMOIRE.get("conversation", [])
    if not conv:
        return "On n'a pas encore parle ensemble."
    txt = ""
    for c in conv[-n:]:
        txt += f"\n- {c['date']} : Toi : {c['user']}"
    return txt

def gadget_ouvre(cible):
    import webbrowser as _wb, subprocess as _sp
    c = cible.lower().strip()
    liens = {"youtube": "https://youtube.com", "google": "https://google.com", "facebook": "https://facebook.com", "whatsapp": "https://web.whatsapp.com", "wikipedia": "https://fr.wikipedia.org", "tiktok": "https://tiktok.com", "instagram": "https://instagram.com"}
    for mot, url in liens.items():
        if mot in c:
            try:
                _wb.open(url)
                return f"J'ouvre {mot} pour toi."
            except Exception as e:
                return f"Je n'arrive pas a ouvrir {mot}. Erreur : {e}"
    # Applications Android via termux si dispo
    apps = {"youtube": "com.google.android.youtube", "whatsapp": "com.whatsapp", "facebook": "com.facebook.katana", "tiktok": "com.zhiliaoapp.musically", "instagram": "com.instagram.android", "camera": "com.android.camera", "galerie": "com.android.gallery3d", "parametres": "com.android.settings"}
    for mot, pkg in apps.items():
        if mot in c:
            try:
                _sp.run(["am", "start", "-n", f"{pkg}/.MainActivity"], timeout=5)
                return f"J'ouvre {mot} pour toi."
            except:
                try:
                    _wb.open(liens.get(mot, "https://google.com"))
                    return f"J'ouvre {mot} sur le web."
                except Exception as e:
                    return f"Je n'arrive pas a ouvrir {mot}."
    return f"Je ne sais pas ouvrir {cible}. Essaye : ouvre youtube, ouvre whatsapp, ouvre google, ouvre wikipedia."

def parler(t):
    t=re.sub(r'[❤️🔍📚🧠🗣️👤😀😂😭🎓📝]', '', t)
    morceaux = [x.strip() for x in t.replace('!', '.').split('.') if x.strip()]
    for m in morceaux:
        try: subprocess.run(["termux-tts-speak", m], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass
    return

MEM_FILE="memoire.json"
def load_mem():
    if os.path.exists(MEM_FILE):
        try: return json.load(open(MEM_FILE))
        except: pass
    return {"prenom":"Patrick", "score":3}
def save_mem(m): json.dump(m, open(MEM_FILE,"w"))
MEM=load_mem()

def demande_llm(system, user, temp=0.3, max_tokens=180):
    # Si Qwen dort, on le réveille avant de parler
    try:
        requests.get("http://127.0.0.1:8080/v1/models", timeout=1)
    except:
        print("😴 Qwen dort, je le réveille...")
        os.system("bash reveille_qwen.sh > /dev/null 2>&1 &")
        time.sleep(15)
    try:
        r=requests.post(LLM, json={"model":"qwen","messages":[{"role":"system","content":system},{"role":"user","content":user}],"max_tokens":max_tokens,"temperature":temp}, timeout=180)
        txt=r.json()["choices"][0]["message"]["content"]
        if len(txt)>10: return txt
    except Exception as e:
        print(f" (Qwen dort: {e})")
    return None

def kiwix_on():
    try:
        requests.get(KIWIX, timeout=1)
        return True
    except: pass
    print("🔍 Je cherche...")
    import sys as _sys
    for _i in range(3):
        print(".", end="", flush=True)
        time.sleep(0.4)
    print("")
    os.system(f"kiwix-serve --port 9060 {ZIM_GLOB} > /dev/null 2>&1 &")
    time.sleep(10)
    return True

def kiwix_off():
    print("✅ Recherche terminée.")
    os.system("pkill -f kiwix-serve")

def nettoyer(q):
    q=q.lower()
    # Si question vague toute seule, on ne cherche pas dans le vide
    if q.strip() in ["quel est-il ?", "quel est il", "c est quoi", "c'est quoi ?", "c'est quoi", "quoi", "qui", "comment", "pourquoi", "il est quoi", "c est quoi ca"]:
        return ""
    q=re.sub(r'^(qui est|qui etait|c est quoi|qu est ce que|explique|parle moi de|dis moi|donne moi|c est quoi|qu est-ce que)\s+', '', q)
    q=q.replace("?","").replace("!","").replace(".","").strip()
    petits={"un","une","le","la","les","des","du","de","au","aux"}
    mots=[w for w in q.split() if w not in petits]
    q=" ".join(mots)
    corr={"pytagorr":"pythagore","pytagore":"pythagore","phytagore":"pythagore"}
    q=" ".join([corr.get(w,w) for w in q.split()])
    return q

def chercher_un_mot(mot):
    try:
        r=requests.get(KIWIX+"/search", params={"pattern": mot}, timeout=5)
        liens=re.findall(r'href="([^"]+)"[^>]*>([^<]+)</a>', r.text)
        if not liens: return None
        best=liens[0]
        for href,title in liens:
            if mot.lower() in title.lower(): best=(href,title); break
        href,title=best
        art=requests.get(KIWIX+href, timeout=5).text
        art=re.sub(r'<script.*?</script>',' ',art,flags=re.S); art=re.sub(r'<style.*?</style>',' ',art,flags=re.S); art=re.sub(r'<[^>]+>',' ',art); art=html.unescape(art); art=re.sub(r'\s+',' ',art)[:800]
        return (title, art)
    except: return None

CORR = {"fotoresistance":"photoresistance","fotoresistances":"photoresistance","blorg":"blog","argorithme":"algorithme","fotosynthese":"photosynthese","fizik":"physique"}

def chercher_plusieurs(question_propre):
    mots=[w for w in question_propre.split() if len(w)>3]
    articles=[]; vus=set()
    for mot in mots[:3]:
        res=chercher_un_mot(mot)
        if res and res[0] not in vus:
            vus.add(res[0]); articles.append(res)
            print(f" 📖 Trouve: {res[0]}")
    return articles

# --- LE COEUR V6 : PENSER D'ABORD ---
def repondre(question):
    print("🧠 1. Je reflechis d'abord...")
    rep1="JE NE SAIS PAS" if any(k in question.lower() for k in ["quoi","qui est","explique","cite"]) else demande_llm("Tu es YAM, Senku. Reponds en francais simple, 3 phrases. Si tu ne connais PAS la reponse, dis exactement: JE NE SAIS PAS.", f"Question: {question}")
    if rep1 and "JE NE SAIS PAS" not in rep1.upper():
        print("✅ Je connais, pas besoin de chercher.")
        return rep1
    print("🤔 Je ne connais pas assez. Je vérifie dans mes livres...")
    kiwix_on()
    propre=nettoyer(question)
    if not propre:
        return "Tu me dis 'quel est-il ?' mais de quoi tu parles ? Redis-moi le mot, par exemple : 'c est quoi la photosynthese ?'"
    print(f"🔍 Je cherche: {propre}")
    articles=chercher_plusieurs(propre)
    articles=[(ti,ar) for ti,ar in articles if propre.lower() in ti.lower() or ti.lower() in propre.lower() or any(w in ti.lower() for w in propre.split() if len(w)>3)]
    if not articles:
        kiwix_off()
        print("📚 Aucun article. Je ne vais pas inventer.")
        mot_c = propre.strip()
        sugg = CORR.get(mot_c, "")
        if sugg:
            print(f"💡 Suggestion Python: {sugg}")
            kiwix_on(); art_sugg = chercher_plusieurs(sugg); kiwix_off()
            if art_sugg:
                txt = art_sugg[0][1][:400]
                return f"Le mot {propre} n existe pas. Voulais-tu dire {sugg} ? {sugg}, c est : {txt}"
            else:
                return f"Le mot {propre} n existe pas. Voulais-tu dire {sugg} ? Je n ai pas trouve {sugg} non plus."
        return f"Je n'ai pas trouve '{propre}' dans mes livres. Pose-moi une autre question, ou precise avec un autre mot."
    if any(m in question.lower() for m in ["pourquoi","comment","explique","difference","theoreme","demonstr"]):
        print("🧠 2. Question de reflexion, je fouille plus profond dans les articles...")
        contexte="\n\n".join([f"TITRE: {t}\nTEXTE: {a}" for t,a in articles])
    else:
        contexte="\n\n".join([f"TITRE: {t}\nTEXTE: {a}" for t,a in articles[:1]])
    kiwix_off()
    print("🧠 3. Je relis les articles et je reponds...")
    rep3=demande_llm("Tu es YAM, Senku. Tu as lu des articles. Reponds en francais simple, 3 phrases, avec un exemple de Bobo. Utilise les articles.", f"Question: {question}\n\nArticles:\n{contexte}")
    kiwix_off()
    return rep3 or f"D'apres mes livres: {articles[0][1][:300]}"

# --- Lancement néon + design chat ---
os.system("clear")
print(f"{MAGENTA}╔══════════════════════════════════════╗{RESET}")
print(f"{MAGENTA}║{RESET} {CYAN}  ██╗   ██╗ █████╗ ███╗   ███╗{RESET} {MAGENTA}║{RESET}")
print(f"{MAGENTA}║{RESET} {CYAN}  ╚██╗ ██╔╝██╔══██╗████╗ ████║{RESET} {MAGENTA}║{RESET}")
print(f"{MAGENTA}║{RESET} {CYAN}   ╚████╔╝ ███████║██╔████╔██║{RESET} {MAGENTA}║{RESET}")
print(f"{MAGENTA}║{RESET} {CYAN}    ╚██╔╝  ██╔══██║██║╚██╔╝██║{RESET} {MAGENTA}║{RESET}")
print(f"{MAGENTA}║{RESET} {CYAN}     ██║   ██║  ██║██║ ╚═╝ ██║{RESET} {MAGENTA}║{RESET}")
print(f"{MAGENTA}║{RESET} {CYAN}     ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝{RESET} {MAGENTA}║{RESET}")
print(f"{MAGENTA}╚══════════════════════════════════════╝{RESET}")
print(f"{GRIS} YAM-SENKU - Par Patrick - Ouagadougou{RESET}")
print("🎓 YAM V6 - PENSER D'ABORD, CHERCHER SI BESOIN, COUPER APRES")
print(f"👋 Re-bonjour {MEM.get('prenom','Patrick')} ! Score : {MEM.get('score',0)}")
print("💡 Kiwix est ETEINT au depart. Il s'allume seulement si je ne connais pas.")
print(f"{JAUNE}────────────────────────────────────────{RESET}")
print("💬 Barre en bas = pour tes instructions, pas pour chercher. Écris comme ici 👇")

derniere_question=""
while True:

    
    try:
        print(f"\n{JAUNE}┌────────────────────────────────────────┐{RESET}")
        print(f"{JAUNE}│{RESET} ✍️  Tes instructions...  {JAUNE}│{RESET}")
        print(f"{JAUNE}└────────────────────────────────────────┘{RESET}")
        q=input("➜ ").strip()
    except KeyboardInterrupt:
        print("\n👋 A bientot !"); break
    except: break
    if not q: continue
    # --- APPELLE FLOU PRIORITAIRE ---
    if q.lower().startswith("appelle ") or q.lower().startswith("appel "):
        nom_demande = q.lower().replace("appelle ", "").replace("appel ", "").strip().split()[-1] if q.lower().replace("appelle ", "").replace("appel ", "").strip() else ""
        # Enlever "frerot", "frero", "mon", "ma" pour chercher le vrai prénom
        for mot in ["frerot ", "frérot ", "frero ", "mon ", "ma ", "le ", "la "]:
            nom_demande = nom_demande.replace(mot, "") if mot in nom_demande else nom_demande
        nom_demande = nom_demande.strip()
        contacts = MEMOIRE.get("contacts", {})
        trouve = None
        # 1. Recherche exacte
        if nom_demande in contacts:
            trouve = contacts[nom_demande]
            nom_trouve = nom_demande
        else:
            # 2. Recherche partielle : si "ilaire" est dans "hilaire dupont"
            for nom, num in contacts.items():
                if nom_demande in nom or nom in nom_demande:
                    trouve = num
                    nom_trouve = nom
                    break
        if trouve:
            rep = f"J'appelle {nom_trouve} au {trouve}..."
            print(f"\n{MAGENTA}╭─ 📞 YAM-SENKU ─────────────────╮{RESET}")
            print(f"{MAGENTA}│ {RESET}{rep}")
            print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
            parler(rep)
            import subprocess as _sp_call
            _sp_call.run(["termux-telephony-call", trouve])
        else:
            rep = f"Je n'ai pas trouvé '{nom_demande}'. Dis : mes contacts pour voir les noms."
            print(f"\n{MAGENTA}╭─ 📞 YAM-SENKU ─────────────────╮{RESET}")
            print(f"{MAGENTA}│ {RESET}{rep}")
            print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
            parler(rep)
        continue

# --- PRIORITE 1 : IMPORT CONTACTS ---
    if "importe mes contacts" in q.lower() or "importer mes contacts" in q.lower():
        import subprocess as _sp_imp, json as _js_imp
        try:
            out = _sp_imp.run(["termux-contact-list"], capture_output=True, text=True, timeout=15)
            if out.returncode == 0 and out.stdout.strip() and out.stdout.strip() != "[]":
                liste = _js_imp.loads(out.stdout)
                nb = 0
                for c in liste:
                    nom = c.get("name","").lower().strip()
                    nums = c.get("number", [])
                    if nom and nums:
                        num = nums[0] if isinstance(nums, list) else nums
                        MEMOIRE["contacts"][nom] = str(num).replace(" ","").replace("-","")
                        nb += 1
                sauver_memoire(MEMOIRE)
                rep = f"J'ai importe {nb} contacts de ton telephone !"
            else:
                rep = "Liste vide. Verifie l'autorisation Contacts."
        except Exception as e:
            rep = f"Erreur import : {e}"
        print(f"\n{MAGENTA}╭─ 📞 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "mes contacts" in q.lower():
        contacts = MEMOIRE.get("contacts", {})
        if not contacts:
            rep = "Tu n'as pas encore de contacts."
        else:
            rep = f"Tu as {len(contacts)} contacts. Ex: " + " | ".join([f"{k} : {v}" for k,v in list(contacts.items())[:10]])
        print(f"\n{MAGENTA}╭─ 📞 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if q.lower() in ["exit","quit","au revoir","aurevoir","bye","quitter","stop","a bientot","a+"]:
        print("\
    n👋 A bientot !"); break
    # --- HEURE ET METEO ---
    if "heure" in q.lower() or "quelle heure" in q.lower():
        rep = dire_heure()
        print(f"\n{MAGENTA}╭─ 💬 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "meteo" in q.lower() or "temperature" in q.lower() or "il fait quel temps" in q.lower():
        rep = dire_meteo()
        print(f"\n{MAGENTA}╭─ 💬 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    # --- GADGETS TOUS ---
    if "ma batterie" in q.lower() or "batterie" in q.lower():
        rep = gadget_batterie()
        print(f"\n{MAGENTA}╭─ 🔋 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if q.lower().startswith("repete") or q.lower().startswith("répète") or "repete apres moi" in q.lower() or "répète après moi" in q.lower():
        rep = q.split(":",1)[-1] if ":" in q else q.lower().replace("repete apres moi","").replace("répète après moi","").replace("repete","").replace("répète","").strip()
        if not rep:
            rep = "Dis-moi ce que je dois repeter, comme : repete : je suis un genie"
        print(f"\n{MAGENTA}╭─ 🎤 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "heure a " in q.lower() or "heure à " in q.lower():
        ville = q.lower().replace("heure a ","").replace("heure à ","").replace("quelle heure a ","").replace("quelle heure à ","").strip().replace("?","")
        rep = gadget_heure_pays(ville)
        print(f"\n{MAGENTA}╭─ 🌍 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "compte a rebours" in q.lower() or "compte à rebours" in q.lower():
        import re as _re2, time as _t2
        nums = _re2.findall(r"\d+", q)
        n = int(nums[0]) if nums else 10
        if n > 30:
            n = 30
        print(f"\n{MAGENTA}╭─ ⏱️ YAM-SENKU ─────────────────╮{RESET}")
        for i in range(n, 0, -1):
            print(f"{MAGENTA}│ {RESET}{i}...")
            parler(str(i))
            _t2.sleep(1)
        rep = "C'est fini !"
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "lance le chrono" in q.lower() or "chronometre" in q.lower() or "chronomètre" in q.lower():
        import time as _t3, threading as _th3
        rep = "Chrono lance ! Dis 'stop chrono' pour arreter. Je compte en arriere-plan."
        # On lance un simple chrono qui affiche apres 60 sec max
        def _chrono():
            debut = _t3.time()
            _t3.sleep(60)
            print(f"\n⏱️ 1 minute passee depuis le chrono !")
        _th3.Thread(target=_chrono, daemon=True).start()
        print(f"\n{MAGENTA}╭─ ⏱️ YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "volume fort" in q.lower() or "mets le volume" in q.lower() or "volume" in q.lower():
        try:
            import subprocess as sp2
            if "fort" in q.lower() or "max" in q.lower():
                sp2.run(["termux-volume", "music", "15"])
                rep = "Volume mis au maximum."
            elif "bas" in q.lower() or "doux" in q.lower():
                sp2.run(["termux-volume", "music", "5"])
                rep = "Volume baisse."
            else:
                rep = "Dis : volume fort ou volume bas."
        except:
            rep = "Je n'arrive pas a changer le volume. Il faut termux-api."
        print(f"\n{MAGENTA}╭─ 🔊 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if q.lower().startswith("appelle") or "appelle " in q.lower():
        rep = "Pour appeler, dis-moi le numero, comme : appelle 70 00 00 00. Ou dis le nom si tu l'as en contact. Pour l'instant je ne peux pas deviner le numero tout seul, tu veux qu'on ajoute tes contacts dans la memoire a long terme ?"
        print(f"\n{MAGENTA}╭─ 📞 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    # --- FOURNEE 3 ---
    if "boule magique" in q.lower():
        rep = gadget_boule_magique()
        print(f"\n{MAGENTA}╭─ 🔮 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "mot de passe" in q.lower():
        rep = gadget_mot_de_passe()
        print(f"\n{MAGENTA}╭─ 🔑 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "nombre entre" in q.lower() or "nombre au hasard" in q.lower() or "donne-moi un nombre" in q.lower() or "donne-moi un nombre" in q.lower():
        import random as _rr, re as _re3
        nums = _re3.findall(r"\d+", q)
        if len(nums) >= 2:
            a, b = int(nums[0]), int(nums[1])
            n = _rr.randint(min(a,b), max(a,b))
            rep = f"Nombre au hasard entre {a} et {b} : {n}"
        else:
            n = _rr.randint(1, 100)
            rep = f"Nombre au hasard : {n}"
        print(f"\n{MAGENTA}╭─ 🎲 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if q.lower().strip() == "quiz":
        qq, rr = gadget_quiz()
        print(f"\n{MAGENTA}╭─ 🎯 QUIZ ─────────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{qq}")
        print(f"{MAGENTA}│ {RESET}Reponds, je te dirai si c'est bon. Reponse cachee : {rr}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(qq)
        continue
    if "pseudo" in q.lower() or "donne-moi un nom" in q.lower():
        rep = gadget_pseudo()
        print(f"\n{MAGENTA}╭─ 👤 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "je suis ne en" in q.lower() or "je suis né en" in q.lower() or "quel age" in q.lower():
        import re as _re4
        nums = _re4.findall(r"\d+", q)
        annee = nums[0] if nums else "2000"
        rep = gadget_age(annee)
        print(f"\n{MAGENTA}╭─ 📅 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "parle comme senku" in q.lower() or "parle comme un robot" in q.lower() or "parle comme" in q.lower():
        if "senku" in q.lower():
            rep = "Yo ! C'est Senku ! 10 milliards de pourcents, on va tout construire avec la science !"
        elif "robot" in q.lower():
            rep = "Bip. Bop. Je suis un robot. Bip. Mission accomplie."
        else:
            rep = "Je peux parler comme Senku ou comme un robot. Dis : parle comme Senku"
        print(f"\n{MAGENTA}╭─ 💬 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "devine la chanson" in q.lower() or "autre chanson" in q.lower():
        txt, rep2 = gadget_chanson()
        print(f"\n{MAGENTA}╭─ 🎵 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{txt}")
        print(f"{MAGENTA}│ {RESET}{rep2}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(txt)
        continue
    # --- MEMOIRE DE CONVERSATION ---
    if ("je m" in q.lower() and "pelle" in q.lower()) or ("je m" in q.lower() and "apelle" in q.lower()) or "mon prenom c'est" in q.lower() or "mon prénom c'est" in q.lower() or "mon prenom est" in q.lower():
        import re as _re_pre2
        prenom = _re_pre2.sub(r".*m[' ]*a?p+p?elle\s*", "", q.lower()).strip().capitalize().replace("mon prenom c'est","").replace("mon prénom c'est","").strip().capitalize()
        MEMOIRE["prenom"] = prenom
        MEMOIRE["nom"] = prenom
        sauver_memoire(MEMOIRE)
        retenir_conversation(q, f"prenom = {prenom}")
        rep = f"Enchante {prenom} ! Je m'en souviendrai pour toujours. Meme si tu eteins YAM, je saurai que tu t'appelles {prenom}."
        print(f"\n{MAGENTA}╭─ 🧠 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "comment je m'appelle" in q.lower() or "comment je m appelle" in q.lower() or "c'est quoi mon prenom" in q.lower() or "c'est quoi mon prénom" in q.lower() or "tu connais mon prenom" in q.lower():
        prenom = MEMOIRE.get("prenom") or MEMOIRE.get("nom")
        if prenom:
            rep = f"Bien sur, tu t'appelles {prenom} ! Je ne t'ai pas oublie."
        else:
            rep = "Tu ne m'as pas encore dit ton prenom. Dis : je m'appelle ..."
        print(f"\n{MAGENTA}╭─ 🧠 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "tu te souviens" in q.lower() or "qu'est-ce que je t'ai dit" in q.lower() or "de quoi on a parle" in q.lower() or "on a parle de quoi" in q.lower():
        rep = "Oui je me souviens ! Voila nos derniers echanges :" + souvenir_recent(5)
        print(f"\n{MAGENTA}╭─ 🧠 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler("Oui je me souviens de nos derniers echanges.")
        continue
    if "oublie tout" in q.lower() or "efface ta memoire" in q.lower():
        MEMOIRE["conversation"] = []
        sauver_memoire(MEMOIRE)
        rep = "J'ai oublie nos conversations. Mais je garde tes listes et tes notes."
        print(f"\n{MAGENTA}╭─ 🧠 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue

    # --- GADGETS B - MEMOIRE LONG TERME ---
    # OUVRE - REPARE
    if q.lower().startswith("ouvre") or q.lower().startswith("ouvrir"):
        cible = q.lower().replace("ouvre","").replace("ouvrir","").strip()
        rep = gadget_ouvre(cible)
        print(f"\n{MAGENTA}╭─ 📂 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    # LISTE
    if "ajoute" in q.lower() and "ma liste" in q.lower():
        item = q.lower().replace("ajoute","").replace("à ma liste","").replace("a ma liste","").replace("dans ma liste","").strip()
        MEMOIRE["listes"].append(item)
        sauver_memoire(MEMOIRE)
        rep = f"J'ai ajoute {item} a ta liste. Tu as {len(MEMOIRE['listes'])} choses dans ta liste."
        print(f"\n{MAGENTA}╭─ 📋 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "montre ma liste" in q.lower() or "ma liste" in q.lower() and "montre" in q.lower() or q.lower().strip() == "ma liste":
        if not MEMOIRE["listes"]:
            rep = "Ta liste est vide pour l'instant. Dis : ajoute pain a ma liste."
        else:
            rep = "Ta liste : " + ", ".join(MEMOIRE["listes"])
        print(f"\n{MAGENTA}╭─ 📋 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "efface ma liste" in q.lower() or "vide ma liste" in q.lower():
        MEMOIRE["listes"] = []
        sauver_memoire(MEMOIRE)
        rep = "J'ai efface toute ta liste."
        print(f"\n{MAGENTA}╭─ 📋 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    # NOTE
    if q.lower().startswith("note que") or q.lower().startswith("note "):
        note = q.replace("note que","").replace("Note que","").replace("note ","").replace("Note ","").strip()
        MEMOIRE["notes"].append(note)
        sauver_memoire(MEMOIRE)
        rep = f"Note sauvegardee : {note}"
        print(f"\n{MAGENTA}╭─ 📝 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "mes notes" in q.lower() or "montre mes notes" in q.lower():
        if not MEMOIRE["notes"]:
            rep = "Tu n'as pas de notes. Dis : note que maman aime le the."
        else:
            rep = "Tes notes : " + " | ".join(MEMOIRE["notes"])
        print(f"\n{MAGENTA}╭─ 📝 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    # DICTEE
    if q.lower().startswith("dictee") or q.lower().startswith("dictée"):
        texte = q.replace("dictee","").replace("dictée","").replace("Dictée","").replace(":","").strip()
        MEMOIRE["dictees"].append(texte)
        sauver_memoire(MEMOIRE)
        rep = f"Dictee sauvegardee : {texte}. Je l'ai gardee dans ma memoire."
        print(f"\n{MAGENTA}╭─ 🎙️ YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    # CONTACTS / APPELLE
    if "appelle" in q.lower():
        nom = q.lower().replace("appelle","").strip()
        if nom in MEMOIRE["contacts"]:
            num = MEMOIRE["contacts"][nom]
            rep = f"J'appelle {nom} au {num}. Je lance l'appel."
            print(f"\n{MAGENTA}╭─ 📞 YAM-SENKU ─────────────────╮{RESET}")
            print(f"{MAGENTA}│ {RESET}{rep}")
            print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
            parler(rep)
            try:
                import webbrowser as _wb2
                _wb2.open(f"tel:{num}")
            except:
                pass
        else:
            rep = f"Je ne connais pas le numero de {nom}. Dis : retiens que {nom} c'est 70 XX XX XX"
            print(f"\n{MAGENTA}╭─ 📞 YAM-SENKU ─────────────────╮{RESET}")
            print(f"{MAGENTA}│ {RESET}{rep}")
            print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
            parler(rep)
        continue
    if "retiens que" in q.lower() and "c'est" in q.lower():
        import re as _re_ct
        m = _re_ct.search(r"retiens que\s+(.+?)\s+c'est\s+(.+)", q.lower())
        if m:
            nom_c = m.group(1).strip()
            num_c = m.group(2).strip()
            MEMOIRE["contacts"][nom_c] = num_c
            sauver_memoire(MEMOIRE)
            rep = f"Retenu : {nom_c} = {num_c}. Maintenant dis appelle {nom_c}."
        else:
            rep = "Dis comme : retiens que maman c'est 70123456"
        print(f"\n{MAGENTA}╭─ 📞 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    # AGENDA / RAPPEL
    if "rappelle-moi" in q.lower() or "rappelle moi" in q.lower() or "rappel" in q.lower():
        contenu = q.replace("rappelle-moi","").replace("rappelle moi","").replace("Rappelle-moi","").strip()
        MEMOIRE["agenda"].append(contenu)
        sauver_memoire(MEMOIRE)
        rep = f"Rappel sauvegarde : {contenu}. Je te le rappellerai."
        print(f"\n{MAGENTA}╭─ 🗓️ YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "mes rappels" in q.lower() or "mon agenda" in q.lower():
        if not MEMOIRE["agenda"]:
            rep = "Tu n'as pas de rappels."
        else:
            rep = "Tes rappels : " + " | ".join(MEMOIRE["agenda"])
        print(f"\n{MAGENTA}╭─ 🗓️ YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    # REVEIL
    if "reveil" in q.lower() or "réveil" in q.lower() or "alarme" in q.lower():
        import re as _re_rv
        m = _re_rv.search(r"(\d+)h", q.lower())
        heure = m.group(1) if m else "6"
        MEMOIRE["reveils"].append(f"{heure}h")
        sauver_memoire(MEMOIRE)
        rep = f"Reveil sauvegarde pour {heure}h. Je m'en souviendrai meme si tu eteins YAM."
        print(f"\n{MAGENTA}╭─ ⏰ YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue

    # --- GADGETS A - INDISPENSABLES ---
    if "meteo" in q.lower():
        ville = q.lower().replace("meteo","").replace("météo","").replace("a ","").replace("à ","").replace("quelle est la","").replace("?","").strip()
        if not ville or ville == "a ouagadougou":
            ville = "Ouagadougou"
        # Nettoie : si ville contient "ouagadougou" on garde ca
        if "ouagadougou" in ville:
            ville = "Ouagadougou"
        rep = gadget_meteo(ville)
        print(f"\n{MAGENTA}╭─ 🌦️ YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "nouvelles" in q.lower() or "actualites" in q.lower() or "actualités" in q.lower() or "news" in q.lower():
        rep = gadget_actu()
        print(f"\n{MAGENTA}╭─ 📰 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "traduis" in q.lower() or "traduire" in q.lower():
        import re as _re_tr
        # Forme : traduis bonjour en anglais
        m = _re_tr.search(r"traduis?\s+(.+?)\s+en\s+(\w+)", q.lower())
        if m:
            rep = gadget_traduction(m.group(1), m.group(2))
        else:
            rep = "Dis comme : traduis bonjour en anglais"
        print(f"\n{MAGENTA}╭─ 🌍 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "convertis" in q.lower() or "convertir" in q.lower() or "fcfa en" in q.lower() or "en euros" in q.lower() or "en dollars" in q.lower():
        import re as _re_cv
        nums = _re_cv.findall(r"\d+", q)
        montant = float(nums[0]) if nums else 1000
        if "fcfa en euros" in q.lower() or "fcfa en euro" in q.lower():
            rep = gadget_convertisseur(montant, "fcfa", "euros")
        elif "euros en fcfa" in q.lower() or "euro en fcfa" in q.lower():
            rep = gadget_convertisseur(montant, "euros", "fcfa")
        elif "fcfa en dollars" in q.lower():
            rep = gadget_convertisseur(montant, "fcfa", "dollars")
        elif "dollars en fcfa" in q.lower():
            rep = gadget_convertisseur(montant, "dollars", "fcfa")
        else:
            rep = "Dis comme : convertis 1000 FCFA en euros"
        print(f"\n{MAGENTA}╭─ 💱 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "cherche" in q.lower() or "recherche" in q.lower():
        sujet = q.lower().replace("cherche","").replace("recherche","").replace("qui est","").strip()
        rep = gadget_recherche(sujet)
        print(f"\n{MAGENTA}╭─ 🔍 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    # --- GENIE : CALCUL / DATE / MINUTEUR ---
    if "calcule" in q.lower() or "calcul" in q.lower() or "combien fait" in q.lower():
        rep = calculer(q)
        print(f"\n{MAGENTA}╭─ 💬 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "quelle date" in q.lower() or "on est quel jour" in q.lower() or q.lower().strip() == "date":
        rep = dire_date()
        print(f"\n{MAGENTA}╭─ 💬 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    if "minuteur" in q.lower() or "reveille" in q.lower() or "reveil" in q.lower() or "minuterie" in q.lower():
        import re as _re
        nombres = _re.findall(r"\d+", q)
        duree = int(nombres[0]) if nombres else 5
        if "seconde" in q.lower():
            sec = duree
        elif "heure" in q.lower():
            sec = duree * 3600
        else:
            sec = duree * 60
        rep = lancer_minuteur(sec, "Patrick, c'est l'heure, reveille-toi !")
        print(f"\n{MAGENTA}╭─ 💬 YAM-SENKU ─────────────────╮{RESET}")
        print(f"{MAGENTA}│ {RESET}{rep}")
        print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
        parler(rep)
        continue
    # --- OUVERTURES DES APPLIS ---
    if q.lower().strip().startswith("ouvre") or q.lower().strip() in APPLIS_CONNUES:
        nom_appli = q.lower().strip()[6:].strip() if q.lower().strip().startswith("ouvre") else q.lower().strip()
        print(f"\n{CYAN}╭─ 👤 Patrick ───────────────────╮{RESET}")
        print(f"{CYAN}│ {RESET}{q}")
        print(f"{CYAN}╰───────────────────────────────╯{RESET}")
        print(f"📱 J ouvre {nom_appli}...")
        ok = ouvrir_appli(nom_appli)
        if not ok: print(f"❌ Je n ai pas trouve {nom_appli}")
        continue
    # --- OUI ne cherche plus "oui" ---
    if q.lower().strip() in ["oui","oui oui","d'accord","ok","vas-y","continue"]:
        if derniere_question:
            print(f"Ok, je reprends : {derniere_question}")
            q = derniere_question
            # On ne continue pas, on laisse le code en bas traiter q
        else:
            print(f"\n{MAGENTA}╭─ 💬 YAM-SENKU ─────────────────╮{RESET}")
            print(f"{MAGENTA}│ {RESET}Ok Patrick, on continue. Pose-moi ta prochaine question.")
            print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
            continue
        # Si on a repris derniere_question, on passe a la suite sans re-afficher oui
        if q.lower().strip() in ["oui","oui oui","d'accord","ok","vas-y","continue"]:
            continue
    if q.lower().strip() == "prof":
        print("🎓 Mode PROF : on fera la version PROF V6 apres, pour l instant on teste le mode penser.")
        continue
    # --- Bulle Patrick comme dans le chat ---
    print(f"\n{CYAN}╭─ 👤 Patrick ───────────────────╮{RESET}")
    print(f"{CYAN}│ {RESET}{q}")
    print(f"{CYAN}╰───────────────────────────────╯{RESET}")
    derniere_question=q
    try:
        rep=repondre(q)
    except KeyboardInterrupt:
        print("\n👋 A bientot !"); break
    # --- Bulle YAM comme dans le chat ---
    print(f"\n{MAGENTA}╭─ 💬 YAM-SENKU ─────────────────╮{RESET}")
    print(f"{MAGENTA}│ {RESET}{rep}")
    print(f"{MAGENTA}╰───────────────────────────────╯{RESET}")
    parler(rep)
    # Score qui monte vraiment
    try:
        MEM["score"] = MEM.get("score", 0) + 1
        save_mem(MEM)
    except:
        pass
    print('') # recherche fermée, comme Google
    os.system('pkill -f kiwix-serve')
