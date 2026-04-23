from .base import Crawler


class XyeBBSCrawler(Crawler):
    netloc: str = "xyebbs.com"

    @classmethod
    async def _updateInfo(cls, url: str) -> dict[str, str]:
        soup = await cls._get_page_with_playwright(url)
        result = {
            "URL": url,
            "name": "",
            "version": "",
            "date": "",
            "log": "",
        }
        if name_element := soup.find("div", class_="flex flex-col md:flex-row md:gap-1 md:items-end"):
            result["name"] = name_element.text.strip()
        if version_element := soup.find("span", class_="z-20 text-base font-bold"):
            result["version"] = version_element.text.split("-", maxsplit=1)[1].strip()
        if date_element := soup.find("span", class_="z-20 text-xs text-gray-500"):
            result["date"] = date_element.text.strip()
        if log_element := soup.find("div", class_="markdown-body"):
            result["log"] = cls._html2markdown(log_element)

        return result
