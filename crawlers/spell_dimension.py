from bs4 import BeautifulSoup, Tag

from .base import Crawler


def get_between_first_two_h2(soup: BeautifulSoup) -> Tag:
    """获取所有标签（按文档顺序，包括嵌套）"""
    h2s = soup.find_all("h2")
    if len(h2s) < 2:
        return soup.new_tag("div")
    elements, current = [], h2s[0]
    while (current := current.next_sibling) and current != h2s[1]:
        if isinstance(current, Tag):   # 只收集标签，忽略文本节点
            elements.append(current)
    parent = soup.new_tag("div")
    parent.extend(elements)
    return parent

class SpellDimensionCrawler(Crawler):
    netloc: str = "karashok-leo.github.io/Wiki/zh/spell-dimension/changelog"

    @classmethod
    async def _updateInfo(cls, url: str) -> dict[str, str]:
        soup = await cls._get_page_with_aiohttp(url)
        result = {
            "URL": url,
            "name": "咒次元",
            "version": "",
            "date": "",
            "log": "",
        }
        if version_and_date_element := soup.find("h2"):
            text = version_and_date_element.text.replace("-", "").split()
            if len(text) > 0:
                result["version"] = text[0].strip()
            if len(text) > 1:
                result["date"] = text[1].strip()
        result["log"] = cls._html2markdown(get_between_first_two_h2(soup))
        return result
