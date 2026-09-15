import os
import re
import requests
import trafilatura
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.tools import tool
from readability import Document

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


logger = logging.getLogger(__name__)


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web and return a list of relevant results.

    Use this when you need up-to-date information, facts not in your
    training data, or sources to cite. Do not use it for purely
    computational or reasoning tasks.

    Args:
        query: The search query. Short, specific phrases (2-6 words)
            work better than full sentences.
        max_results: Maximum number of results to return (default 5).

    Returns:
        A string with one block per result, each containing the
        title, URL, and a snippet of the page content, separated by
        '---'. Returns a message stating no results were found if the
        search returns nothing, or a message describing the failure
        if the search itself errors out.
    """
    try:
        results = tavily.search(query=query, max_results=max_results)
    except Exception as exception:
        logger.exception("web_search failed for query=%r", query)
        return f"Search failed: {exception}"

    hits = results.get("results", [])
    if not hits:
        return f"No results found for query: {query!r}"

    output = []
    for result in hits:
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        content = result.get("content", "")
        snippet = content[:300] + ("..." if len(content) > 300 else "")
        output.append(f"Title: {title}\nUrl: {url}\nSnippet: {snippet}\n")

    return "\n---\n".join(output)


@tool
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text

        extracted = trafilatura.extract(
            html, include_comments=False, include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r"\s+", " ", extracted)
            return cleaned[:5000]

        document = Document(html)
        clean_html = document.summary()

        soup = BeautifulSoup(clean_html, "html.parser")

        tags = ["script", "style", "nav", "footer", "header", "aside", "form"]

        for tag in soup(tags):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r"\s+", " ", text)
            return cleaned[:5000]

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(tags):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        cleaned = re.sub(r"\s+", " ", text)

        if cleaned:
            return cleaned[:5000]

        return "Could not extract meaningful content from the page."

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."

    except requests.exceptions.HTTPError as exception:
        return f"HTTP error occurred: {str(exception)}"

    except Exception as exception:
        return f"Could not scrape URL: {str(exception)}"
