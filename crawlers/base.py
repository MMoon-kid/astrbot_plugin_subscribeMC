from abc import ABC, abstractmethod
from typing import Dict
from bs4 import BeautifulSoup


class Crawler(ABC):
    @classmethod
    @abstractmethod
    async def updateInfo(cls, url: str) -> Dict[str, str]:
        raise NotImplementedError

    @classmethod
    def _html2markdown(cls, html: BeautifulSoup) -> str:
        result = []
        for child in html.children:
            if isinstance(child, str):
                text = child.strip()
                if text:
                    result.append(text)
            elif child.name:
                if child.name == 'h1':
                    result.append(f"# {child.get_text().strip()}")
                elif child.name == 'h2':
                    result.append(f"## {child.get_text().strip()}")
                elif child.name == 'h3':
                    result.append(f"### {child.get_text().strip()}")
                elif child.name == 'h4':
                    result.append(f"#### {child.get_text().strip()}")
                elif child.name == 'h5':
                    result.append(f"##### {child.get_text().strip()}")
                elif child.name == 'h6':
                    result.append(f"###### {child.get_text().strip()}")
                elif child.name == 'p':
                    text = child.get_text().strip()
                    if text:
                        result.append(text)
                elif child.name == 'li':
                    text = child.get_text().strip()
                    if text:
                        result.append(f"- {text}")
                elif child.name == 'ol':
                    for i, li in enumerate(child.find_all('li', recursive=False), 1):
                        text = li.get_text().strip()
                        if text:
                            result.append(f"{i}. {text}")
                elif child.name == 'ul':
                    for li in child.find_all('li', recursive=False):
                        text = li.get_text().strip()
                        if text:
                            result.append(f"- {text}")
                elif child.name == 'a':
                    text = child.get_text().strip()
                    href = child.get('href', '')
                    if href:
                        result.append(f"[{text}]({href})")
                    else:
                        result.append(text)
                elif child.name == 'strong' or child.name == 'b':
                    result.append(f"**{child.get_text().strip()}**")
                elif child.name == 'em' or child.name == 'i':
                    result.append(f"*{child.get_text().strip()}*")
                elif child.name == 'code':
                    result.append(f"`{child.get_text().strip()}`")
                elif child.name == 'br':
                    result.append('\n')
                elif child.name == 'div':
                    result.append(cls._html2markdown(child))
                elif child.name == 'span':
                    result.append(child.get_text().strip())
                else:
                    result.append(cls._html2markdown(child))
        return '\n'.join(result)
