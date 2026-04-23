from .base import Crawler
from .bbsmc import BBSMCCrawler
from .github import GitHubCrawler
from .mcmod import MCModCrawler
from .modrinth import ModrinthCrawler
from .spell_dimension import SpellDimensionCrawler
from .xyebbs import XyeBBSCrawler

__all__ = [
    "Crawler",
    "BBSMCCrawler",
    "GitHubCrawler",
    "MCModCrawler",
    "ModrinthCrawler",
    "SpellDimensionCrawler",
    "XyeBBSCrawler",
]
