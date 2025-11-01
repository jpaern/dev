from typing import List, Tuple
import urllib3
from lxml import html
from loguru import logger
from bs4 import BeautifulSoup

http = urllib3.PoolManager()
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass

import pandas as pd


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


def position_to_class(pos: int) -> str:
    return valid_classes()[pos]


def class_to_position(clas: str) -> str:
    if not clas.startswith("/"):
        clas = "/" + clas
    if not clas.endswith("/"):
        clas = clas + "/"
    return valid_classes().index(clas)


def get_subclass(url: str) -> str:
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
    logger.debug(f"Crawling {url}")
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


def process_date(date: str, base_url: str) -> list[Line]:
    """
    Process one date: crawl the URL, then get the details for each result,
    and return a list of Line objects.
    """
    logger.info(f"Processing {date}")
    url = base_url + date
    res = crawl(url, valid_classes())
    lines = []
    total = len(res)
    for i, r in enumerate(res):
        ymd = get_year_month_day(date)
        logger.debug(f"  {i+1}/{total} Processing {r[2]}")
        text = get_page(r[2])
        line = Line(
            category=r[0],
            sub_category=r[1],
            text=text,
            year=ymd.year,
            month=ymd.month,
            day=ymd.day,
        )
        lines.append(line)
    return lines


def process_date_wrapper(args):
    """
    Unpack arguments and call process_date. Return a tuple (date, lines).
    This function is defined at the module level so it's pickleable.
    """
    date, base_url = args
    lines = process_date(date, base_url)
    return date, lines


def main():
    dates = get_list_of_dates("2025-01-01", "2025-08-31")
    base_url = "https://www.tagesschau.de/archiv?datum="

    # Prepare a list of argument tuples for each process_date call.
    args = [(date, base_url) for date in dates]

    # Dictionary to track for each month if we've already written a header.
    monthly_files_written = {}

    # Process each date in parallel.
    with mp.Pool(processes=2) as pool:
        for date, lines in tqdm(
            pool.imap_unordered(process_date_wrapper, args),
            total=len(args),
            desc="Processing dates",
        ):
            # Assume date is in the format "YYYY-MM-DD"; extract "YYYY-MM"
            year_month = date[:7]
            filename = f"data/news_{year_month}.csv"
            df = pd.DataFrame(lines)
            # Write header only if this is the first time writing for this month.
            write_header = not monthly_files_written.get(year_month, False)
            # Append the day's data to the monthly file.
            df.to_csv(filename, mode="a", header=write_header, index=False)
            monthly_files_written[year_month] = True
            # logger.info(f"Appended results for {date} to {filename}")


if __name__ == "__main__":
    main()
