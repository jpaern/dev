from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

import pandas as pd
from pandas import DataFrame
import requests
import urllib3
from bs4 import BeautifulSoup
from loguru import logger
from lxml import html

http = urllib3.PoolManager()


@dataclass
class Line:
    ausland: bool = False
    faktenfinder: bool = False
    investigativ: bool = False
    inland: bool = False
    wirtschaft: bool = False
    wissen: bool = False
    sub_category: str | None = None
    text: str = ""
    year: str = ""
    month: str = ""
    day: str = ""

    def __init__(
        self,
        category: str,
        sub_category: str | None = None,
        text: str = "",
        year: str = "",
        month: str = "",
        day: str = "",
    ):
        # Convert the provided category to lowercase for case-insensitive matching.
        category_lower = category.lower()

        self.ausland = "ausland" in category_lower
        self.faktenfinder = "faktenfinder" in category_lower
        self.investigativ = "investigativ" in category_lower
        self.inland = "inland" in category_lower
        self.wirtschaft = "wirtschaft" in category_lower
        self.wissen = "wissen" in category_lower
        self.sub_category = sub_category
        self.text = text
        self.year = year
        self.month = month
        self.day = day


@dataclass
class YMD:
    year: str
    month: str
    day: str


def valid_classes() -> List[str]:
    return [
        "/ausland/",
        "/faktenfinder/",
        "/inland/",
        "/investigativ/",
        "/wirtschaft/",
        "/wissen/",
    ]


def get_class(url: str) -> str | None:
    parts = url.split("/")
    res = None
    if len(parts) > 1:
        res = parts[1]

    return res


def get_subclass(url: str) -> str | None:
    parts = url.split("/")
    res = None
    if len(parts) > 3:
        res = parts[2]

    return res


def get_category(ref: str, valid_classes) -> str | None:
    for cl in valid_classes:
        if cl in ref:
            return get_class(ref)
    return None


def crawl(
    url: str, valid_classes: List[str], prefix: str = "https://www.tagesschau.de"
):
    logger.info(f"Crawling {url}")
    r = requests.get(url)
    data_string = r.text
    tree = html.fromstring(data_string)
    links = tree.xpath("//a")
    res = []
    for link in links:
        ref = link.get("href")
        cat = get_category(ref, valid_classes)
        if cat and ref.endswith(".html"):
            subclass = get_subclass(ref)
            res.append((cat, subclass, prefix + ref))
    return res


def get_page(url: str) -> str:
    # logger.debug(f"  Processing url: {url}")
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


def save_texts(df: DataFrame, file_name: str) -> None:
    df.to_csv(file_name)


def main():
    df = pd.DataFrame()
    dates = get_list_of_dates("2024-01-01", "2024-01-02")
    base_url = "https://www.tagesschau.de/archiv?datum="
    data = []
    for date in dates:
        logger.info(f"Processing {date}")
        url = base_url + date
        res = crawl(url, valid_classes())
        length = len(res)
        logger.info(f"Length: {length}")
        for i, r in enumerate(res):
            ymd = get_year_month_day(date)
            logger.debug(f"  {i+1}/{length} Processing {r[2]}")
            text = get_page(r[2])
            line = Line(
                category=r[0],
                sub_category=r[1],
                text=text,
                year=ymd.year,
                month=ymd.month,
                day=ymd.day,
            )
            data.append(line)
    df = DataFrame(data)
    df.to_csv("third.csv")


if __name__ == "__main__":
    main()
