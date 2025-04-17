import aiohttp
import asyncio
import time
import os
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
    logger.info(f"Starting task: {url}")
    async with session.get(url) as response:
        data = await response.json()
        logger.info(f"Got data: {data}")
        if response.status != 200:
            logger.error(f"Error fetching data: {response.status}")
            return None
        return data


def fetch_urls(search_data: dict) -> list:
    urls = []
    if 'items' in search_data:
        for item in search_data['items']:
            if 'link' in item:
                urls.append(item['link'])
    return urls


def clean_html(content: str) -> str:
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text(separator=' ', strip=True)


async def fetch_single_page(session, url):
    """Fetch content from a single URL and clean it"""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                raw_html = await response.text()
                cleaned_text = clean_html(raw_html)
                return {"page_url": url, "content": cleaned_text}
            else:
                logger.error(f"Error fetching URL {url}: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Exception fetching URL {url}: {str(e)}")
        return None


async def fetch_page_content(list_of_urls: list) -> list:
    """Fetch content from multiple URLs concurrently"""
    connector = aiohttp.TCPConnector(limit_per_host=5)
    connector._max_header_field_size = 32768  # Increase header size

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_single_page(session, url) for url in list_of_urls]
        return await asyncio.gather(*tasks)


async def google_search(search_query: str):
    base_url = f"https://www.googleapis.com/customsearch/v1?key={os.getenv('GOOGLE_CUSTOM_SEARCH_API')}&cx={os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')}"
    query_result: dict
    final_result: list[dict]

    async with aiohttp.ClientSession() as session:
        query_result = await fetch_data(session, base_url + f"&q={search_query}")
        logger.info("Got result!")

    if query_result is None:
        return None

    urls = fetch_urls(query_result)
    logger.info(f"Got urls: {urls}")
    final_result = await fetch_page_content(urls)
    logger.info("Got final result!")
    return final_result