from .base import Crawler


class MCModCrawler(Crawler):
    netloc: str = "mcmod.cn"

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
        if name_element := soup.find("title"):
            result["name"] = name_element.text.split("更新日志")[0].strip()
        if date_element := soup.find("span", class_="time"):
            result["date"] = date_element.text.strip()
        if version_element := soup.find("span", class_="name"):
            result["version"] = version_element.text.strip()
        if log_element := soup.find("div", class_="content common-text font14"):
            result["log"] = cls._html2markdown(log_element)
        return result
