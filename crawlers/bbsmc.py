from .base import Crawler


class BBSMCCrawler(Crawler):
    netloc: str = "bbsmc.net"

    @classmethod
    async def _updateInfo(cls, url: str) -> dict[str, str]:
        soup = await cls._get_page_with_aiohttp(url)
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
            # print(date_element)
            if (date_element := date_element.find_all("span")) and len(date_element) > 0:
                result["date"] = date_element[-1].text.replace("on", "").strip()
        if log_element := soup.find("div", class_="markdown-body"):
            result["log"] = cls._html2markdown(log_element)
        return result
