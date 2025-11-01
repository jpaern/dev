from typing import List

import urllib3
from bs4 import BeautifulSoup
from loguru import logger
from lxml import html

http = urllib3.PoolManager()
from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd
import requests


@dataclass
class Line:
    category: List[int]
    sub_category: str
    text: str
    year: str
    month: str
    day: str


@dataclass
class YMD:
    year: str
    month: str
    day: str


def valid_classes() -> List[str]:
    return [
        "/ausland/",
        "/inland/",
        "/wirtschaft/",
        "/wissen/",
        "/investigativ/",
        "/faktenfinder/",
    ]


def position_to_class(pos: int) -> str:
    return valid_classes()[pos]


def class_to_position(clas: str) -> int:
    if not clas.startswith("/"):
        clas = "/" + clas
    if not clas.endswith("/"):
        clas = clas + "/"
    return valid_classes().index(clas)


def get_subclass(url: str) -> str:
    parts = url.split("/")
    res = ""
    if len(parts) > 2:
        res = parts[2]

    return res


def crawl(
    url: str, valid_classes: List[str], prefix: str = "https://www.tagesschau.de"
):
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
            subclass = get_subclass(l)
            int_list = list(map(int, ls))
            res.append((int_list, subclass, prefix + l))
    return res


def get_page(url: str) -> str:
    logger.info(f"Processing url: {url}")
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    paragraphs = soup.find_all("p", class_="textabsatz")
    first = True
    res = ""
    for text in paragraphs:
        res += text.get_text()
        if first:
            res = "<strong>" + res + "</strong>"
        first = False
    return res


def get_list_of_dates(start_date: str, end_date: str) -> List[str]:
    """
    Returns a list of date strings between start_date_str and end_date_str
    inclusive.

    Parameters:
        start_date_str (str): The start date in "YYYY-MM-DD" format.
        end_date_str (str): The end date in "YYYY-MM-DD" format.

    Returns:
        list of str: A list of dates between start and end date, each in
        "YYYY-MM-DD" format.
    """
    # Convert the string dates to datetime.date objects
    sd = datetime.strptime(start_date, "%Y-%m-%d").date()
    ed = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Calculate the difference in days between the dates
    delta = ed - sd

    # Generate a list of date strings for all days between the start and end
    # date (inclusive)
    dates = [
        (sd + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)
    ]

    return dates


def get_year_month_day(date: str) -> YMD:
    parts = date.split("-")
    return YMD(year=parts[0], month=parts[1], day=parts[2])


def save_texts(texts: List[str], class_array: List[int], base_path: str) -> None:
    for text in texts:
        pass


def main():
    df = pd.DataFrame()
    dates = get_list_of_dates("2024-01-01", "2024-03-01")
    base_url = "https://www.tagesschau.de/archiv?datum="
    for date in dates:
        __import__("ipdb").set_trace()
        logger.info(f"Processing {date}")
        url = base_url + date
        res = crawl(url, valid_classes())
        logger.info(f"Length: {len(res)}")
        for r in res:
            ymd = get_year_month_day(date)
            line = Line(
                category=r[0],
                sub_category=r[1],
                text=r[2],
                year=ymd.year,
                month=ymd.month,
                day=ymd.day,
            )
            df.append(line)


if __name__ == "__main__":
    main()
