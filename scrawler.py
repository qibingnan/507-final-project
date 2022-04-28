
import json
import time
from typing import Callable, Dict, List, Optional, Tuple, TypeVar


import requests
from bs4 import BeautifulSoup, Tag

from movies import Movie

TimeGap = 15
Session = requests.session()
Url = 'https://www.imdb.com/search/title/?groups=top_1000'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
Headers = {'User-Agent': UA}


class Parser:

    @staticmethod
    def year(wrapper: Tag) -> int:
        """Parse year for remove redudant scope.

        - year: '(2013)'
        - [return]: 2013

        Default value: ``0``.
        """
        if wrapper.text.strip('()').isdigit():
            return int(wrapper.text.strip('()'))
        return 0

    @staticmethod
    def duration(wrapper: Tag) -> int:
        """Parse duration time.

        - duration: '130 min'
        - [return]: 130

        Default value: ``0``.
        """
        if wrapper.text.strip(' min').isdigit():
            return int(wrapper.text.rstrip(' min'))
        return 0

    @staticmethod
    def categories(wrapper: Tag) -> List[str]:
        """Parse categories."""
        return wrapper.text.strip().split(', ')

    @staticmethod
    def rating(wrapper: Tag) -> float:
        """Parse rating from string.

        Default value: ``0.0``
        """
        try:
            return float(wrapper.text.strip())
        except ValueError:
            return 0.

    @staticmethod
    def description(wrapper: Tag) -> str:
        """Parse description."""
        return wrapper.text.strip()

    @staticmethod
    def votes(wrapper: Tag) -> int:
        """Parser votes.

        Default value: ``0``.
        """
        votes = wrapper.attrs.get('data-value', '0')
        if votes.isdigit():
            return int(votes)
        return 0

    @staticmethod
    def idname(wrapper: Tag) -> Tuple[str, str]:
        """Parse id and name."""
        if wrapper.a and isinstance(wrapper.a, Tag):
            href = wrapper.a.attrs.get('href', '//')
            if not href.count('/') >= 2:
                link = ''
            else:
                link = href.split('/')[2]
            return link, wrapper.a.text
        return '', ''

    @staticmethod
    def casts(wrapper: Tag) -> Tuple[str, List[str]]:
        """Parse director and stars."""
        director, actors = '', []
        for index, name in enumerate(wrapper.find_all('a')):
            if index == 0:
                director = name.text
            else:
                actors.append(name.text)
        return director, actors


T = TypeVar('T')


def find(div: Tag,
         callback: Callable[[Tag], T],
         name: Optional[str] = None,
         attrs: Optional[Dict[str, str]] = None,
         subnodes: Optional[List[str]] = None) -> T:
    """Find node and call handler for taking info."""
    current = div
    subnodes = [] if not subnodes else subnodes
    if attrs:
        current = div.find(name=name, attrs=attrs)
    for nodename in subnodes:
        if not current:
            raise ValueError('Node not exists.')
        current = getattr(div, nodename)
    if not isinstance(current, Tag):
        raise ValueError('Node type error.')
    return callback(current)


def parse(html: str) -> List[Movie]:
    """Parse single page."""

    soup = BeautifulSoup(html, features="lxml")
    divs: List[Tag] = soup.find_all(class_='lister-item-content')
    movies = []

    for div in divs:
        try:
            id_, name = find(div, Parser.idname, subnodes=['h3'])
            description = Parser.description(
                div.find_all('p', attrs={'class': 'text-muted'})[1])
            rating = find(div, Parser.rating, attrs={
                          'class': 'ratings-imdb-rating'}, subnodes=['strong'])
            votes = find(div, Parser.votes, attrs={'name': 'nv'})
            year = find(div, Parser.year, attrs={
                        'class': 'lister-item-year'})
            director, stars = find(
                div, Parser.casts, name='p', attrs={'class': ''})
            categories = find(div, Parser.categories,
                              attrs={'class': 'genre'})
            duration = find(div, Parser.duration,
                            attrs={'class': 'runtime'})
        except (ValueError, IndexError):
            continue
        movies.append(Movie(id_, name, description, rating, votes,
                      year, director, stars, categories, duration))
    return movies


def page(start: int) -> List[Movie]:
    """Get page movies."""
    url = Url + f'&start={start}'
    response = Session.get(url, headers=Headers)
    if not response.status_code == 200:
        return []
    return parse(response.text)


if __name__ == '__main__':
    movies: List[Movie] = []
    for start in range(1, 1000, 50):
        movies.extend(page(start))
        print(
            f'Page {start // 50 + 1} finished, current downloaded: {len(movies)}.')
        time.sleep(TimeGap)

    with open('movies.json', 'w') as handler:
        _movies = [movie.dump() for movie in movies]
        json.dump(_movies, handler, ensure_ascii=False, indent=4)
