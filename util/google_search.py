import asyncio
import io
import time
import os

import aiohttp
from starlette.concurrency import run_in_threadpool
import pdfplumber
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from bs4 import BeautifulSoup


from util.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

"""
    Taken from geeksforgeeks
    https://www.geeksforgeeks.org/asynchronous-http-requests-with-python/

    I made my own changes on the code since I am going to use this
    for custom google search engine api calls.
"""


async def fetch_data(session, url):
    async with session.get(url) as response:
        data = await response.json()
        logger.info(f"Got data: {data}")
        if response.status != 200:
            logger.error(f"Error fetching data: {response.status}")
            return None
        return data


def fetch_urls(search_data: dict) -> list:
    urls: list = []
    if 'items' in search_data:
        for item in search_data['items']:
            if 'link' in item:
                urls.append(item['link'])
    return urls


def clean_html(content: str) -> str:
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text(separator=' ', strip=True)


async def fetch_single_page(session, url):
    """Fetch content from a single HTML URL and clean it"""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                try:
                    raw_html = await response.text()
                except UnicodeDecodeError:
                    raw_bytes = await response.read()
                    for encoding in ['utf-8', 'iso-8859-1', 'windows-1252', 'latin1']:
                        try:
                            raw_html = raw_bytes.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        logger.warning(f"Could not decode content from {url}")
                        return None

                cleaned_text = await run_in_threadpool(clean_html, raw_html)
                return {"page_url": url, "content": cleaned_text, "role": "Google Search"}
            else:
                logger.error(f"Error fetching URL {url}: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Exception fetching URL {url}: {str(e)}")
        return None


async def fetch_page_content(list_of_urls: list) -> list:
    """Fetch content from multiple URLs concurrently"""
    connector = aiohttp.TCPConnector(limit_per_host=20)
    connector._max_header_field_size = 32768  # Increase header size

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_single_page(session, url) for url in list_of_urls]
        return await asyncio.gather(*tasks)


async def google_search(search_query: str):
    """
       Sample response for google_search:
       [
           {
               "page_url": "https://example.com/page1",
               "content": "This is the cleaned text content from page 1...",
               "role": "Google Search"
           },
           {
               "page_url": "https://example.com/page2.pdf",
               "content": "This is the extracted text from the PDF on page 2...",
               "role": "Google Search"
           },
           {
               "page_url": "https://anotherexample.org/article",
               "content": "Article text cleaned and extracted...",
               "role": "Google Search"
           },
           None, # Could be None if a particular URL fetch failed
           {
               "page_url": "https://example.com/page3",
               "content": "More content from another page...",
               "role": "Google Search"
           }
       ]
      Or None if the initial Google Custom Search API call fails.
   """
    key = os.getenv('GOOGLE_CUSTOM_SEARCH_API')
    cx = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    base_url = f"https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&num=5"

    logger.info(f"Search query: {search_query}")

    async with aiohttp.ClientSession() as session:
        query_result = await fetch_data(session, base_url + f"&q={search_query}")

    if not query_result:
        return None

    urls = fetch_urls(query_result or {})
    urls = list(dict.fromkeys(urls))[:10]

    logger.info(f"Got urls: {urls}")
    final_result = await fetch_page_content(urls)
    logger.info("Got final result!")
    return final_result