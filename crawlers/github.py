from .base import Crawler


class GitHubCrawler(Crawler):
    netloc: str = "github.com"

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
        if name_element := soup.find("a", {
            "data-pjax": "#repo-content-pjax-container",
            "data-turbo-frame": "repo-content-turbo-frame"
        }):
            if name_element.get("class", None) is None:
                result["name"] = name_element.text.strip()
        if version_element := soup.find("h1", class_="tmp-mr-3 d-inline"):
            result["version"] = version_element.text.strip().removeprefix(result["name"]).strip()
        if date_element := soup.find("relative-time", class_="no-wrap"):
            result["date"] = date_element.get("datetime", "").strip()
        if log_element := soup.find("div", class_="markdown-body"):
            result["log"] = cls._html2markdown(log_element)
        return result
