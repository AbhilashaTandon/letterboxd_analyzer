import psycopg2

from items import ReviewItem


def main():
    self.connection = psycopg2.connect(
        "dbname='letterboxd' user='postgres' host='localhost' password='j?NzWpZEYHqv(bL87%4*C=kw'")

    self.current = self.connection.cursor()

    # Create quotes table if none exists
    self.current.execute("""DROP TABLE IF EXISTS users CASCADE;
                                DROP TABLE IF EXISTS movies CASCADE;
                                DROP TABLE IF EXISTS reviews CASCADE;

                                CREATE TABLE users(
                                    id SERIAL,
                                    name VARCHAR(128) UNIQUE,
                                    PRIMARY KEY(id)
                                );

                                CREATE TABLE movies(
                                    id INTEGER UNIQUE,
                                    name VARCHAR(128),
                                    PRIMARY KEY(id)
                                ); 
                                -- dont make key serial here, since we're using letterboxd's ids and not adding movies in their order. also movie names might not be unique

                                CREATE TABLE reviews(
                                    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
                                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                                    rating INTEGER,
                                    PRIMARY KEY(movie_id, user_id)
                                );""")

    items = []

    review = ReviewItem()
    review['user'] = "Bob"
    review['name'] = "St. Elmo's Fire"
    review['movie_id'] = 125232
    review['rating'] = 7

    items.append(review)

    review = ReviewItem()
    review['user'] = "Arjun"
    review['name'] = "St. Elmo's Fire"
    review['movie_id'] = 125232
    review['rating'] = 3

    items.append(review)

    review = ReviewItem()
    review['user'] = "Bob"
    review['name'] = "Jaws"
    review['movie_id'] = 105239
    review['rating'] = 5

    items.append(review)

    review = ReviewItem()
    review['user'] = "Nushi"
    review['name'] = "Jaws"
    review['movie_id'] = 105239
    review['rating'] = 10

    items.append(review)

    review = ReviewItem()
    review['user'] = "Bob"
    review['name'] = "The Sixth Sense"
    review['movie_id'] = 924
    review['rating'] = 2

    items.append(review)

    review = ReviewItem()
    review['user'] = "Arjun"
    review['name'] = "The Sixth Sense"
    review['movie_id'] = 924
    review['rating'] = 4

    items.append(review)

    review = ReviewItem()
    review['user'] = "Nushi"
    review['name'] = "The Sixth Sense"
    review['movie_id'] = 924
    review['rating'] = 7

    items.append(review)

    for item in items:
        self.current.execute("""INSERT INTO movies (id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING;""", (
            item["movie_id"],
            item["name"],
        ))

        self.current.execute(
            "INSERT INTO users (name) VALUES (%s) ON CONFLICT DO NOTHING;", (item["user"],))

        self.current.execute(
            "SELECT * FROM users WHERE name = %s;", (item["user"],))

        result = self.current.fetchone()

        user_id = 0  # placeholder

        if (result is None):
            raise RuntimeError("error adding user to users table")
        else:
            user_id = result[0]

        if (user_id != 0):
            try:
                self.current.execute("INSERT INTO reviews (movie_id, user_id, rating) VALUES (%s, %s, %s)",
                                     (item["movie_id"], user_id, item["rating"]))
            except psycopg2.errors.UniqueViolation:
                print("Tried to insert duplicate review",
                      item["name"], item["user"], item["rating"])
                return
        else:
            raise RuntimeError("tried to insert with user_id 0")

    self.connection.commit()


if __name__ == "__main__":
    main()
