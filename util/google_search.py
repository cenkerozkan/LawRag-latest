import aiohttp
import asyncio
import time
import os
from dotenv import load_dotenv
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


async def google_search(search_query: str):
    base_url = f"https://www.googleapis.com/customsearch/v1?key={os.getenv('GOOGLE_CUSTOM_SEARCH_API')}&cx={os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')}"

    async with aiohttp.ClientSession() as session:
        result: dict = await fetch_data(session, base_url+f"&q={search_query}")
        logger.info(f"Got result: {result}")


if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(google_search("Kovulunca haklarım"))
    print(f"Total time taken: {time.time() - start_time} seconds")
