import requests
from bs4 import BeautifulSoup


def stars_to_value(rating: str) -> int:  # turns ★★★★½ into 4.5
    value = 0
    for char in rating:
        if (char == '★'):
            value += 1
        elif (char == '½'):
            value += .5
    return int(value * 2)


def get_liked_movies(user: str) -> list:

    movie_data = list()
    for reviews_page in range(1, 1000):
        page = requests.get(
            'https://letterboxd.com/' + user + '/films/by/entry-rating/page/' + str(reviews_page), timeout=1)

        if (not page):  # if bad http response
            return movie_data

        soup = BeautifulSoup(page.text, features="lxml")

        movies = soup.find_all('li', class_='poster-container')

        for movie in movies:
            movie_name = movie.div.img['alt']
            movie_id = movie.div['data-film-id']  # unique
            rating = movie.find('span', class_='rating')
            if (not rating is None):  # rating is none if unreviewed but watched
                user_rating = stars_to_value(
                    rating.text)

                movie_data.append(movie_name + ' ' +
                                  movie_id + ' ' + user + ' ' + str(user_rating))
            else:
                return movie_data  # after first w no review none of the rest will have them

    return movie_data


def main():
    all_users = []

    with open('reviews.csv', mode='a', encoding='utf-8') as output_file:

        for i in range(1, 1000):
            users_url = 'https://letterboxd.com/members/popular/this/all-time/page/' + \
                str(i) + '/'

            users_response = requests.get(users_url, timeout=1)

            if (not users_response):
                break

            users_soup = BeautifulSoup(users_response.text, features="lxml")

            users = [user['href']
                     for user in users_soup.find_all('a', class_='avatar')]

            print(i, len(users), users[0])

            for user in users:
                print(user)
                for review in get_liked_movies(user.replace('/', '')):
                    output_file.write(review + '\n')
                return

            all_users.extend(users)


if __name__ == "__main__":
    main()
