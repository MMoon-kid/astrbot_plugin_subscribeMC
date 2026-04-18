import asyncio
from bs4 import BeautifulSoup
from typing import Dict
from .base import Crawler


class XyeBBSCrawler(Crawler):
    @classmethod
    def _get_page_with_selenium(cls, url: str) -> str:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.markdown-body"))
            )
            
            import time
            time.sleep(1)
            
            return driver.page_source
        finally:
            if driver:
                driver.quit()
    
    @classmethod
    async def updateInfo(cls, url: str) -> Dict[str, str]:
        html = await asyncio.to_thread(cls._get_page_with_selenium, url)
        
        soup = BeautifulSoup(html, 'html.parser')
        result = {
            "URL": url,
            "name": "",
            "version": "",
            "date": "",
            "log": "",
        }
        if name_element := soup.find("div", class_="flex flex-col md:flex-row md:gap-1 md:items-end"):
            result["name"] = name_element.text.strip()
        if version_element := soup.find('span', class_="z-20 text-base font-bold"):
            result["version"] = version_element.text.split('-', maxsplit=1)[1].strip()
        if date_element := soup.find('span', class_="z-20 text-xs text-gray-500"):
            result["date"] = date_element.text.strip()
        if log_element := soup.find('div', class_='markdown-body'):
            result["log"] = cls._html2markdown(log_element)
        
        return result
