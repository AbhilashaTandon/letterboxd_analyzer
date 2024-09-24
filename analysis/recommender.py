import numpy as np
import pandas as pd

import re


def filter_out_tv(data):
    love_death_robots_filter = re.compile("love-death-robots")
    black_mirror_filter = re.compile("black-mirror")

    to_be_removed = []

    for idx, row in data.iterrows():
        if (re.match(love_death_robots_filter, row['name'])):
            to_be_removed.append(idx)
        elif (re.match(black_mirror_filter, row['name'])):
            to_be_removed.append(idx)

    return data.drop(to_be_removed)


def look_up_movie(movie_name, unique_movies):
    match_string = re.compile(".*" + movie_name + ".*")
    for idx, (movie_id, movie_name) in enumerate(unique_movies):
        # movie_name = movie_id_to_name[movie_id]
        if (re.match(match_string, movie_name)):
            yield (movie_name, movie_id, idx)


def get_similar_movies(movie_name, n, movie_name_to_idx, similarities, movie_names):
    idx = movie_name_to_idx[movie_name]
    similarities = similarities[idx]

    sim_movies_idxs = np.argpartition(similarities, -(n+1))[-(n+1):][::-1]

    sim_movies_names = [movie_names[idx] for idx in sim_movies_idxs]

    movie_similarities = [similarities[idx] for idx in sim_movies_idxs]

    for name, sim in sorted(zip(sim_movies_names, movie_similarities), key=lambda x: x[1], reverse=True)[1:]:
        yield (name, sim)


def main():
    data = pd.read_csv("reviews.csv")

    data = filter_out_tv(data)

    # print(data.head(10))

    unique_movies = sorted(list(set(zip(data['movie_id'], data['name']))))

    unique_users = sorted(list(set(data['user_id'])))

    num_movies = len(unique_movies)
    num_users = len(unique_users)

    # print("%d Unique Movies" % num_movies)
    # print("%d Unique Users" % num_users)

    movie_id_to_idx = {movie_id: idx for idx,
                       (movie_id, _) in enumerate(unique_movies)}

    user_id_to_idx = {user_id: idx for idx, user_id in enumerate(unique_users)}

    movie_name_to_idx = {movie_name: idx for idx,
                         (_, movie_name) in enumerate(unique_movies)}

    movie_names = [movie_name for (_, movie_name) in unique_movies]

    movie_id_to_name = {movie_id: movie_name for (
        movie_id, movie_name) in unique_movies}

    movie_name_to_idx = {
        movie_id_to_name[movie_id]: idx for idx, (movie_id, _) in enumerate(unique_movies)}

    movie_freqs = {movie_id_to_idx[movie_id]: freq for (
        movie_id, freq) in zip(data['movie_id'], data['count_'])}

    ratings = np.ones((num_movies, num_users)) * 5

    for _, row in data.iterrows():
        movie_idx = movie_id_to_idx[row['movie_id']]
        user_idx = user_id_to_idx[row['user_id']]

        ratings[movie_idx, user_idx] = row['rating']

    for idx in range(num_movies):
        ratings_row = ratings[idx]  # making it binary might work better
        nonzero = np.array([x for x in filter(lambda x: x > 0, ratings_row)])
        mean = np.mean(nonzero)
        stdev = np.std(nonzero)
        # ratings_row[ratings_row < threshold] = 0
        # ratings_row[ratings_row >= threshold] = 1
        ratings[idx] = [(rating - mean)/stdev if rating >
                        0 else 0 for rating in ratings_row]
        # ratings[idx] = ratings_row

    freq_vector = np.array([movie_freqs[idx] for idx in range(num_movies)])

    ratings = np.divide(ratings, freq_vector[:, None])

    from sklearn.metrics.pairwise import cosine_similarity

    cos_sim = cosine_similarity(ratings)

    for movie in ["i-saw-the-tv-glow", "but-im-a-cheerleader", "twin-peaks-fire-walk-with-me", "knives-out-2019", "emma-2020"]:
        print(f"Movies similar to {movie}")
        for movie, sim in get_similar_movies(movie, 5, movie_name_to_idx, cos_sim, movie_names):
            print("", movie, sim, sep='\t')
        print()


if __name__ == "__main__":
    main()
