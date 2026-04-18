# 爬虫基础类和工厂
from .base import Crawler
from typing import Dict

from .mcmod import MCModCrawler
from .xyebbs import XyeBBSCrawler
from .bbsmc import BBSMCCrawler

async def updateInfo(url: str) -> Dict[str, str]:
    if 'mcmod.cn' in url:
        return await MCModCrawler.updateInfo(url)
    elif 'xyebbs.com' in url:
        return await XyeBBSCrawler.updateInfo(url)
    elif 'bbsmc.net' in url:
        return await BBSMCCrawler.updateInfo(url)
    else:
        raise ValueError(f"不支持的网站: {url}\n目前支持:\n- mcmod.cn\n- xyebbs.com\n- bbsmc.net")
    

__all__ = ['Crawler', 'updateInfo']
