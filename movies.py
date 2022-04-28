
import json
from dataclasses import dataclass
from typing import List, Dict

from btree import BTree, Serializable


@dataclass
class Movie(Serializable):
    id: str
    name: str
    description: str
    rating: float
    votes: int
    year: int
    director: str
    stars: List[str]
    categories: List[str]
    duration: int

    def __str__(self) -> str:
        lines = ['Moive:']
        for key, value in self.__dict__.items():
            lines.append(f'\t{key}: {value}')
        return '\n'.join(lines)

    def dump(self) -> Dict:
        return self.__dict__.copy()

    @classmethod
    def load(cls, data: Dict):
        return cls(**data)


def load(filename: str) -> List[Movie]:
    movies = []
    with open(filename, 'r') as handler:
        for data in json.load(handler):
            movies.append(Movie.load(data))
    return movies


def maketree(filename: str) -> BTree[str, Movie]:
    tree: BTree[str, Movie] = BTree(11)
    for movie in load(filename):
        tree.insert(movie.id, movie)
    return tree
