from sys import version

import aiohttp
from bs4 import BeautifulSoup
from typing import Dict
from .base import Crawler


class MCModCrawler(Crawler):
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
                name_element = soup.find("title").text.split("更新日志")
                if len(name_element) > 0:
                    result["name"] = name_element[0].strip()
                if date_element := soup.find('span', class_="time"):
                    result["date"] = date_element.text.strip()
                if version_element := soup.find('span', class_="name"):
                    result["version"] = version_element.text.strip()
                if log_element := soup.find('div', class_="content common-text font14"):
                    result["log"] = cls._html2markdown(log_element)
                return result
