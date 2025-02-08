from typing import List
import urllib3
from urllib.request import urlopen
from lxml import html
from loguru import logger
from bs4 import BeautifulSoup
http = urllib3.PoolManager()

def crawl(url: str, valid_classes: List[str], prefix: str = "https://www.tagesschau.de"):
    logger.info(f"Crawling {url}")
    r = http.request("GET", url)
    data_string = r.data.decode("utf-8", errors="ignore")
    tree = html.fromstring(data_string)
    links = tree.xpath("//a")
    res = []
    for link in links:
        # import ipdb; ipdb.set_trace()
        l = link.get("href")
        ls = [s in l for s in valid_classes]
        if any(ls) and l.endswith(".html"):
            res.append(prefix + l)
    return res


def get_page(url: str) -> str:
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()



def main():
    host = "https://www.tagesschau.de/archiv?datum=2025-02-07"
    valid_classes = ["/ausland/", "/inland/", "/wirtschaft/", "/wissen/", "/investigativ/", "/faktenfinder/"]
    res = crawl(host, valid_classes)
    # logger.info(f"Found: {res}")
    logger.info(f"Length: {len(res)}")
    text = get_page(res[0])
    logger.info(f"Text of first url:\n{text}")


if __name__ == "__main__":
    main()
