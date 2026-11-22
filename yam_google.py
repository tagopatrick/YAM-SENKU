import urllib.request, urllib.parse, re, json

def rechercher_google(question, limite=3):
    try:
        q = urllib.parse.quote(question)
        url = f"https://html.duckduckgo.com/html/?q={q}"
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
        
        # extrait les résultats
        titres = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html)
        
        res = []
        for i in range(min(limite, len(titres))):
            t = re.sub('<[^>]+>', '', titres[i])[:100]
            s = re.sub('<[^>]+>', '', snippets[i] if i < len(snippets) else "")[:200]
            res.append(f"- {t}: {s}")
        return "\n".join(res) if res else "Pas de resultat Google"
    except Exception as e:
        return f"Erreur Google: {e}"

if __name__ == "__main__":
    while True:
        q = input("Google test (quit pour sortir): ")
        if q in ["quit","exit"]: break
        print(rechercher_google(q))
