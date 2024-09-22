# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from itemadapter import ItemAdapter
import psycopg2


class LetterboxdPipeline:
    def __init__(self):
        # Connection Details
        self.hostname = 'localhost'
        self.username = 'postgres'
        self.password = "j?NzWpZEYHqv(bL87%4*C=kw"  # your password
        self.database = 'letterboxd'

    def open_spider(self, spider):
        # Create/Connect to database
        try:
            self.connection = psycopg2.connect(
                host=self.hostname, user=self.username, password=self.password, dbname=self.database)
        except:
            print("I am unable to connect to the database")
            raise RuntimeError("Database Connection Error")

        self.current = self.connection.cursor()

        # Create quotes table if none exists
        # self.current.execute("""DROP TABLE IF EXISTS users CASCADE;
        #                             DROP TABLE IF EXISTS movies CASCADE;
        #                             DROP TABLE IF EXISTS reviews CASCADE;

        #                             CREATE TABLE users(
        #                                 id SERIAL,
        #                                 name VARCHAR(128) UNIQUE,
        #                                 PRIMARY KEY(id)
        #                             );

        #                             CREATE TABLE movies(
        #                                 id INTEGER UNIQUE,
        #                                 name VARCHAR(128),
        #                                 PRIMARY KEY(id)
        #                             );
        #                             -- dont make key serial here, since we're using letterboxd's ids and not adding movies in their order. also movie names might not be unique

        #                             CREATE TABLE reviews(
        #                                 movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
        #                                 user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        #                                 rating INTEGER,
        #                                 PRIMARY KEY(movie_id, user_id)
        #                             );""")

        # self.current.execute("""TRUNCATE users, movies, reviews;""")

    def process_item(self, item, spider):
        with open("../log.txt", mode='a') as log_file:
            log_file.write("SQL FETCH %s" % item)

        if (not any(map(lambda x: x is None, item.values()))):

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
                    return item
            else:
                raise RuntimeError("tried to insert with user_id 0")

            try:
                self.current.execute("""INSERT INTO movies (id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING;""", (
                    item["movie_id"],
                    item["name"],
                ))
                self.connection.commit()
            except psycopg2.errors.InFailedSqlTransaction:
                self.connection.rollback()

            self.current = self.connection.cursor()

            try:
                self.current.execute(
                    "INSERT INTO users (name) VALUES (%s) ON CONFLICT DO NOTHING;", (item["user"],))
                self.connection.commit()
            except psycopg2.errors.InFailedSqlTransaction:
                self.connection.rollback()

            self.current = self.connection.cursor()

            self.connection.commit()

        else:
            raise RuntimeError("data contained None")
        return item

    def close_spider(self, spider):

        # Close cursor & connection to database
        self.current.close()
        self.connection.close()


class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open("output.json", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item


'''
SELECT movie_count.movie_id, movie_count.name, movie_count.count_, reviews.user_id, reviews.rating
FROM (
    SELECT reviews.movie_id, movies.name, 
    COUNT(reviews.movie_id) as count_
    FROM reviews JOIN movies ON movies.id = movie_id 
    GROUP BY reviews.movie_id, movies.name 
    ORDER BY Count(reviews.movie_id) DESC LIMIT 6000
) 
movie_count JOIN reviews ON reviews.movie_id = movie_count.movie_id
ORDER BY movie_count.count_;
'''
