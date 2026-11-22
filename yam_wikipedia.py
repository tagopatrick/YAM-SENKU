import urllib.request
from urllib.parse import quote_plus, urljoin, unquote
from html.parser import HTMLParser

BASE = "http://127.0.0.1:8081/"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.ignored += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.ignored:
            self.ignored -= 1

    def handle_data(self, data):
        if not self.ignored:
            clean = " ".join(data.split())
            if clean:
                self.text.append(clean)


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href.startswith("/content/"):
                self.links.append(href)


def get_html(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "YAM-Offline/1.0"}
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8", errors="replace")


def rechercher(question, limite=5):
    url = BASE + "search?pattern=" + quote_plus(question)
    html = get_html(url)

    parser = LinkParser()
    parser.feed(html)

    resultats = []
    vus = set()

    for lien in parser.links:
        page_url = urljoin(BASE, lien)

        if page_url in vus:
            continue
        vus.add(page_url)

        titre = unquote(lien.rsplit("/", 1)[-1]).replace("_", " ")

        try:
            page_html = get_html(page_url)
            page = PageParser()
            page.feed(page_html)

            texte = " ".join(page.text)
            texte = texte[:6000]

            resultats.append({
                "titre": titre,
                "url": page_url,
                "texte": texte
            })

        except Exception as erreur:
            print("Erreur sur", titre, ":", erreur)

        if len(resultats) >= limite:
            break

    return resultats


if __name__ == "__main__":
    question = input("YAM Wikipédia — Sujet à rechercher : ")

    try:
        articles = rechercher(question)

        if not articles:
            print("Aucun article trouvé.")
        else:
            for i, article in enumerate(articles, 1):
                print("\n" + "=" * 45)
                print(i, "-", article["titre"])
                print("=" * 45)
                print(article["texte"][:2000])

    except Exception as erreur:
        print("Erreur :", erreur)
