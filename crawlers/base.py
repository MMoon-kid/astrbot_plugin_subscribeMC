import asyncio
from abc import ABC, abstractmethod

import aiohttp
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


class Crawler(ABC):
    netloc: str
    ALL: list["Crawler"] = []
    _driver = None

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.ALL.append(cls)

    @classmethod
    @abstractmethod
    async def _updateInfo(cls, url: str) -> dict[str, str]:
        raise NotImplementedError

    @classmethod
    async def updateInfo(cls, url: str) -> dict[str, str]:
        for crawler in cls.ALL:
            if crawler.netloc in url:
                return await crawler._updateInfo(url)
        else:
            urls = "\n".join([f"- {crawler.netloc}" for crawler in cls.ALL])
            raise ValueError(f"不支持的网站: {url}\n目前已支持:\n{urls}")

    @classmethod
    async def _get_page_with_aiohttp(cls, url: str) -> BeautifulSoup:
        headers = {
            "User-Agent": UserAgent().random,           # 随机 UA，避免固定特征
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            # "Referer": url if url else "https://github.com/",
        }
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=60) as response:
                    if response.status != 200:
                        return BeautifulSoup("", "html.parser")
                    return BeautifulSoup(await response.text(), "html.parser")
        except asyncio.TimeoutError:
            return BeautifulSoup("", "html.parser")
        except aiohttp.ClientError:
            return BeautifulSoup("", "html.parser")

    @classmethod
    async def _get_page_with_playwright(cls, url: str, selector: str="div.markdown-body") -> BeautifulSoup:
        async with Stealth().use_async(async_playwright()) as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=UserAgent().random)
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector(selector, state="visible", timeout=30000)
            content = await page.content()
            await browser.close()
            return BeautifulSoup(content, "html.parser")

    @classmethod
    def _html2markdown(cls, soup: BeautifulSoup, indent: int = 0) -> str:
        result = []
        for element in soup.children:
            if isinstance(element, str):
                text = element.strip()
                if text:
                    result.append(text)
            elif element.name:
                if element.name == "h1":
                    result.append(f"# {element.get_text().strip()}")
                elif element.name == "h2":
                    result.append(f"## {element.get_text().strip()}")
                elif element.name == "h3":
                    result.append(f"### {element.get_text().strip()}")
                elif element.name == "h4":
                    result.append(f"#### {element.get_text().strip()}")
                elif element.name == "h5":
                    result.append(f"##### {element.get_text().strip()}")
                elif element.name == "h6":
                    result.append(f"###### {element.get_text().strip()}")
                elif element.name == "p":
                    text = element.get_text().strip()
                    if text:
                        result.append(text)
                elif element.name == "li":
                    if element.find("ul") is None:
                        result.append(f"- {element.get_text().strip()}")
                        continue
                    text, ul_text = "", ""
                    for i in element.children:
                        if isinstance(i, Tag) and i.name == "ul":
                            ul_text += cls._html2markdown(i, indent + 1).removesuffix("\n") + "\n"
                        elif isinstance(i, str):
                            text += i.strip()
                        else:
                            text += i.get_text().strip()
                    if text:
                        result.append(f"- {text}")
                    if ul_text:
                        result.append(ul_text.strip())
                elif element.name == "ol":
                    for i, li in enumerate(element.find_all("li", recursive=False), 1):
                        text = li.get_text().strip()
                        if text:
                            result.append(f"{i}. {text}")
                elif element.name == "ul":
                    trueIndent = indent
                    if soup.name == "ul":
                        trueIndent += 1
                    result.append(cls._html2markdown(element, trueIndent))
                elif element.name == "a":
                    text = element.get_text().strip()
                    if href := element.get("href", ""):
                        result.append(f"[{text}]({href})")
                    else:
                        result.append(text)
                elif element.name == "strong" or element.name == "b":
                    result.append(f"**{element.get_text().strip()}**")
                elif element.name == "em" or element.name == "i":
                    result.append(f"*{element.get_text().strip()}*")
                elif element.name == "code":
                    result.append(f"`{element.get_text().strip()}`")
                elif element.name == "br":
                    result.append("\n")
                elif element.name == "div":
                    result.append(cls._html2markdown(element, indent))
                elif element.name == "span":
                    result.append(element.get_text().strip())
                else:
                    result.append(cls._html2markdown(element, indent))
        return "\n".join("  " * indent + i for i in result)
