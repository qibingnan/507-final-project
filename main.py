
import json
from typing import Dict

from analyse import *
from movies import maketree

from matplotlib import pyplot as plt


def draw_plot(data: Dict, title: str, xlabel: str, ylabel: str) -> None:
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.ticklabel_format(style='plain')
    plt.plot(list(data.keys()), list(data.values()))


def draw_pie(data: Dict[str, int], title: str) -> None:
    plt.title(title)
    plt.pie(list(data.values()), labels=list(data.keys()), autopct='%.2f%%')


if __name__ == '__main__':
    tree = maketree('movies.json')
    with open('btree.json', 'w') as handler:
        json.dump(tree.dump(), handler, indent=4)
    mid = input('Search by movie id in most 3 times: ')
    print(tree.find(mid), '\n')

    # Show hotest five stars
    print('Hotest 5 stars:')
    for star, votes in vote_by_stars()[:5]:
        print(f'\t{star}: {votes}')
    print()

    # Show hotest five movies
    print('Hotest 5 movies:')
    for movie, votes in vote_by_movies()[:5]:
        print(f'\t{movie}: {votes}')
    print()

    # Show categories percents
    draw_plot(dict(movies_by_year()), 'Movies By Years',
              xlabel='Year', ylabel='Count')
    plt.show()

    # Show votes by year
    draw_plot(dict(votes_by_year()), 'Votes By Years',
              xlabel='Vote', ylabel='Count')
    plt.show()

    # Show categories percent
    draw_pie(movie_by_categories(), 'Movies By category')
    plt.show()
