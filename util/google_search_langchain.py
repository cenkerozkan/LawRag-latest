import os
from dotenv import load_dotenv

from langchain_google_community import GoogleSearchAPIWrapper
from config.config import GOOGLE_SEARCH_RESULT

load_dotenv()

os.environ["GOOGLE_CSE_ID"] = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_CUSTOM_SEARCH_API")

def run_google_search(query: str) -> list[dict]:
    """
    Runs a Google search using Langchain's GoogleSearchAPIWrapper.

    Returns a list of dicts with "page_url", "content", "role" (like your async google_search).
    NOTE: This version does not fetch full page content or PDF text (only snippets from search results).
    """
    search = GoogleSearchAPIWrapper(k=GOOGLE_SEARCH_RESULT)
    # First, get all metadata for the search results
    metadata: list[dict] = search.results(query=query, num_results=GOOGLE_SEARCH_RESULT)

    results: list[dict] = []
    for item in metadata:
        page_url = item.get("link") or item.get("url")
        content = item.get("snippet") or item.get("description") or ""
        if page_url and content:
            results.append({
                "page_url": page_url,
                "content": content,
                "role": "Google Search"
            })
    return results