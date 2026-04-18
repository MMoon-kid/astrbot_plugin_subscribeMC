import aiohttp
from bs4 import BeautifulSoup
from typing import Dict
from .base import Crawler


class BBSMCCrawler(Crawler):
    @classmethod
    async def updateInfo(cls, url: str) -> Dict[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                result = {
                    "URL": url,
                    "name": "",
                    "version": "",
                    "date": "",
                    "log": "",
                }
                if name_element := soup.find("h1", class_="hero-title"):
                    result["name"] = name_element.text.strip()
                if version_element := soup.find("h2", class_="name"):
                    result["version"] = version_element.text.strip().removeprefix(result["name"]).strip()
                if date_element := soup.find("div", class_="version-header-text"):
                    result["date"] = date_element.find_all('span')[1].text.replace("on", '').strip()
                if log_element := soup.find("div", class_="markdown-body"):
                    result["log"] = cls._html2markdown(log_element)
                return result
