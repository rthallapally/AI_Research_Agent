import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.document_loaders import ArxivLoader
import requests
from bs4 import BeautifulSoup


def search_arxiv(query, max_results=3):
    loader = ArxivLoader(query=query, load_max_docs=max_results)
    return loader.load()


def get_pubmed_abstracts(query, max_results=3):
    try:
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax={max_results}&term={query}&retmode=json"
        ids = requests.get(search_url, timeout=5).json()['esearchresult']['idlist']
        if not ids:
            print("[PubMed] No results found.")
            return []

        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(ids)}&retmode=xml"
        res = requests.get(fetch_url, timeout=5)
        soup = BeautifulSoup(res.content, "xml")
        abstracts = []

        for article in soup.find_all('PubmedArticle'):
            title = article.ArticleTitle.get_text() if article.ArticleTitle else ""
            abstract = article.AbstractText.get_text() if article.AbstractText else ""
            if abstract:
                abstracts.append({'title': title, 'abstract': abstract})

        return abstracts

    except Exception as e:
        print(f"[PubMed Error] {e}")
        return []
