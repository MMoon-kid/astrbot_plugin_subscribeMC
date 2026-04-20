import asyncio
from abc import ABC, abstractmethod

import aiohttp
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent


class Crawler(ABC):
    netloc: str
    ALL: list["Crawler"] = []

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
            raise ValueError(f"不支持的网站: {url}\n目前已支持:\n{'\n'.join([f'- {crawler.netloc}' for crawler in cls.ALL])}")

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
    def _get_page_with_selenium(cls, url: str) -> BeautifulSoup:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        chrome_options = webdriver.chrome.options.Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.markdown-body"))
            )

            import time
            time.sleep(1)

            return BeautifulSoup(driver.page_source, "html.parser")
        finally:
            if driver:
                driver.quit()

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
                        else:
                            text += i.strip()
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
                    result.append(cls._html2markdown(element, indent))
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
