import pprint
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = 'https://news.ycombinator.com'
SCRAPE_URL = f'{BASE_URL}/news'
SCRAPE_SELECTORS = {
    'links': '.titleline > a',
    'subtext': '.subtext',
    'score': '.score'
}
RELATIVE_PATH = 'item?id='


def fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetches the content of the given URL.

    Args:
        url (str): The URL to fetch.
        timeout (int): The timeout for the request in seconds.

    Returns:
        Optional[str]: The content of the page if the request is successful, None otherwise.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def filter_by_points(news: List[Dict[str, str]], points: int) -> List[Dict[str, str]]:
    """
    Filters the news items by a minimum number of points.

    Args:
        news (List[Dict[str, str]]): List of news items.
        points (int): Minimum number of points.

    Returns:
        List[Dict[str, str]]: Filtered list of news items.
    """
    return list(filter(lambda n: n['points'] > points, news))


def sort_news_by_points(news: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Sorts the news items by points in descending order.

    Args:
        news (List[Dict[str, str]]): List of news items.

    Returns:
        List[Dict[str, str]]: Sorted list of news items.
    """
    return sorted(news, key=lambda k: k['points'], reverse=True)


def reduce_top_news(news_links: List[Tag], news_subtexts: List[Tag]) -> List[Dict[str, str]]:
    """
    Reduces the news links and subtexts into a list of news items with title, link, and points.

    Args:
        news_links (List[Tag]): List of BeautifulSoup elements containing news links.
        news_subtexts (List[Tag]): List of BeautifulSoup elements containing news subtexts.

    Returns:
        List[Dict[str, str]]: List of news items with title, link, and points.
    """
    news = []

    for index, item in enumerate(news_links):
        title = item.getText()
        href = item.get('href', None)
        # If the link is a relative path, we need to append the base URL
        if href and href.startswith(RELATIVE_PATH):
            href = f'{BASE_URL}/{href}'
        score = news_subtexts[index].select(SCRAPE_SELECTORS['score'])
        try:
            point = int(score[0].getText().replace(
                ' points', '')) if len(score) > 0 else 0
        except ValueError:
            point = 0
        news.append({'title': title, 'link': href, 'points': point})

    return sort_news_by_points(filter_by_points(news, 99))


def main() -> None:
    """
    Main function to scrape the Hacker News front page and print the top news items.
    """
    page_content = fetch_page(SCRAPE_URL)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')
        links = soup.select(SCRAPE_SELECTORS['links'])
        subtexts = soup.select(SCRAPE_SELECTORS['subtext'])
        top_news = reduce_top_news(links, subtexts)
        pprint.pprint(top_news)
    else:
        print("Failed to retrieve the page content.")


if __name__ == "__main__":
    main()
