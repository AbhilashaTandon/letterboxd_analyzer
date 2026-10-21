from surprise import Dataset, NormalPredictor, Reader
import numpy as np
import pandas as pd
import re
from collections import defaultdict

from surprise import Dataset, SVD


def look_up_movie(movie_name, unique_movies):
    match_string = re.compile(".*" + movie_name + ".*")
    for idx, (movie_id, movie_name) in enumerate(unique_movies):
        # movie_name = movie_id_to_name[movie_id]
        if (re.match(match_string, movie_name)):
            yield (movie_name, movie_id, idx)


def get_predictions(my_ratings, data, num_users, movie_names, movie_name_to_idx, algo):
    # my_ratings =

    my_ratings_set = data.copy(deep=True)

    user_id = num_users

    for movie_name, rating in my_ratings.items():
        if (movie_name not in movie_names):
            continue
        movie_idx = movie_name_to_idx[movie_name]

        my_ratings_set.loc[-1] = [0, movie_idx,
                                  movie_name, 0, user_id, rating]  # adding a row
        my_ratings_set.index = my_ratings_set.index + 1  # shifting index
        my_ratings_set = my_ratings_set.sort_index()  # sorting by index

    recommender_set = Dataset.load_from_df(
        data[["user_id", "movie_id", "rating"]], Reader(rating_scale=(1, 10))).build_full_trainset()

    test_set = recommender_set.build_anti_testset()

    predictions = algo.test(test_set)

    return predictions


def get_top_n(predictions, user_id, n=10):
    """Return the top-N recommendation for given user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        user_id: the id of the user to get predictions for
        n(int): The number of recommendation to output for user. Default
            is 10.

    Returns:
    A dict where keys are movie_ids and values are estimated ratings of movie for user
    """

    # First map the predictions to each user.
    estimated_ratings = {}
    for uid, iid, _, est, _ in predictions:
        if (uid != user_id):
            continue
        estimated_ratings[iid] = est

    # Then sort the predictions for each user and retrieve the k highest ones.

    estimated_ratings = sorted(
        estimated_ratings, key=lambda x: x[1], reverse=True)
    return estimated_ratings[:n]


def main():
    data = pd.read_csv("reviews_filtered.csv")

    print(data.head(10))

    unique_movies = sorted(list(set(zip(data['movie_id'], data['name']))))

    unique_users = sorted(list(set(data['user_id'])))

    num_movies = len(unique_movies)
    num_users = len(unique_users)

    print("%d Unique Movies" % num_movies)
    print("%d Unique Users" % num_users)

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

    from sklearn.model_selection import train_test_split

    reader = Reader(rating_scale=(1, 10))

    dataset = Dataset.load_from_df(
        data[["user_id", "movie_id", "rating"]], reader).build_full_trainset()

    algo = SVD()

    algo.fit(dataset)

    predictions = get_predictions({"cars": 10, "cars-2": 10, "cars-3": 10},
                                  data, num_users, movie_names, movie_name_to_idx, algo)

    print(get_top_n(predictions, num_users))


if __name__ == "__main__":
    main()
