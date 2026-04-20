from abc import ABC, abstractmethod
import asyncio

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import aiohttp

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
        except asyncio.TimeoutError as e:
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
    def _html2markdown(cls, html: BeautifulSoup) -> str:
        result = []
        for child in html.children:
            if isinstance(child, str):
                text = child.strip()
                if text:
                    result.append(text)
            elif child.name:
                if child.name == "h1":
                    result.append(f"# {child.get_text().strip()}")
                elif child.name == "h2":
                    result.append(f"## {child.get_text().strip()}")
                elif child.name == "h3":
                    result.append(f"### {child.get_text().strip()}")
                elif child.name == "h4":
                    result.append(f"#### {child.get_text().strip()}")
                elif child.name == "h5":
                    result.append(f"##### {child.get_text().strip()}")
                elif child.name == "h6":
                    result.append(f"###### {child.get_text().strip()}")
                elif child.name == "p":
                    text = child.get_text().strip()
                    if text:
                        result.append(text)
                elif child.name == "li":
                    text = child.get_text().strip()
                    if text:
                        result.append(f"- {text}")
                elif child.name == "ol":
                    for i, li in enumerate(child.find_all("li", recursive=False), 1):
                        text = li.get_text().strip()
                        if text:
                            result.append(f"{i}. {text}")
                elif child.name == "ul":
                    for li in child.find_all("li", recursive=False):
                        text = li.get_text().strip()
                        if text:
                            result.append(f"- {text}")
                elif child.name == "a":
                    text = child.get_text().strip()
                    href = child.get("href", "")
                    if href:
                        result.append(f"[{text}]({href})")
                    else:
                        result.append(text)
                elif child.name == "strong" or child.name == "b":
                    result.append(f"**{child.get_text().strip()}**")
                elif child.name == "em" or child.name == "i":
                    result.append(f"*{child.get_text().strip()}*")
                elif child.name == "code":
                    result.append(f"`{child.get_text().strip()}`")
                elif child.name == "br":
                    result.append("\n")
                elif child.name == "div":
                    result.append(cls._html2markdown(child))
                elif child.name == "span":
                    result.append(child.get_text().strip())
                else:
                    result.append(cls._html2markdown(child))
        return "\n".join(result)
