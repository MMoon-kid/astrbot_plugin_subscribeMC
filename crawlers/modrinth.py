import asyncio

from .base import Crawler


class ModrinthCrawler(Crawler):
    netloc: str = "modrinth.com"

    @classmethod
    async def _updateInfo(cls, url: str) -> dict[str, str]:
        soup = await asyncio.to_thread(cls._get_page_with_selenium, url)
        result = {
            "URL": url,
            "name": "",
            "version": "",
            "date": "",
            "log": "",
        }
        if name_element := soup.find("h1", class_="leading-none"):
            result["name"] = name_element.text.strip()
        if version_element := soup.find("h2", class_="name"):
            result["version"] = version_element.text.strip().removeprefix(result["name"]).strip()
        if date_element := soup.find("div", class_="version-header-text"):
            if (date_element := date_element.find_all("span")) and len(date_element) > 0:
                result["date"] = date_element[-1].text.replace("on", "").strip()
        if log_element := soup.find("div", class_="markdown-body"):
            result["log"] = cls._html2markdown(log_element)
        return result
