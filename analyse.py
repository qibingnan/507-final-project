
from collections import defaultdict

from movies import load

movies = load('movies.json')


def movies_by_year():
    """Analyse best movie by year."""
    result = defaultdict(int)
    for movie in movies:
        result[movie.year] += 1
    result.pop(0)
    return sorted(result.items(), key=lambda kv: kv[0])


def votes_by_year():
    """Analyse total votes by year."""
    result = defaultdict(int)
    for movie in movies:
        result[movie.year] += movie.votes
    result.pop(0)
    return sorted(result.items(), key=lambda kv: kv[0])


def movie_by_categories():
    """Count movie in each category."""
    result = defaultdict(int)
    for movie in movies:
        for category in movie.categories:
            result[category] += 1
    result = dict(sorted(result.items(), reverse=False, key=lambda kv: kv[1])[:10])
    return {
        name: int(count / sum(result.values()) * 100) for name, count in result.items()
    }


def vote_by_stars():
    """Find hotest movie star which have highest sum of votes."""
    result = defaultdict(int)
    for movie in movies:
        for star in movie.stars:
            result[star] += movie.votes
    return sorted(result.items(), key=lambda kv: kv[1])


def vote_by_movies():
    """Find hotest movie."""
    return sorted({movie.name: movie.votes for movie in movies}.items(), key=lambda kv: kv[1])
