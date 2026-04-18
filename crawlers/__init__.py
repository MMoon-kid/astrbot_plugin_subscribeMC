from .base import Crawler
from .bbsmc import BBSMCCrawler
from .mcmod import MCModCrawler
from .xyebbs import XyeBBSCrawler


async def updateInfo(url: str) -> dict[str, str]:
    if "mcmod.cn" in url:
        return await MCModCrawler.updateInfo(url)
    elif "xyebbs.com" in url:
        return await XyeBBSCrawler.updateInfo(url)
    elif "bbsmc.net" in url:
        return await BBSMCCrawler.updateInfo(url)
    else:
        raise ValueError(f"不支持的网站: {url}\n目前支持:\n- mcmod.cn\n- xyebbs.com\n- bbsmc.net")


__all__ = ["Crawler", "updateInfo"]
