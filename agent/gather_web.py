from ddgs import DDGS
from bs4 import BeautifulSoup
import requests

# Optional denylist of known-blocking domains
DENYLIST = [
    "sciencedirect.com",
    "weforum.org",
    "zhihu.com",
    "costco.com",
]

def search_web(query, max_results=2):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            url = r['href']
            if any(bad in url for bad in DENYLIST):
                print(f"[Skipped (denylist)] {url}")
                continue
            results.append(url)
    return results


def extract_web_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=3)  # reduced timeout
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        return "\n".join(paragraphs)

    except requests.exceptions.HTTPError as e:
        print(f"[HTTP Error] {url} → {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"[Timeout] {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Request Error] {url} → {e}")
        return None
