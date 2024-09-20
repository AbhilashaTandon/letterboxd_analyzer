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
        hostname = 'localhost'
        username = 'postgres'
        password = "j?NzWpZEYHqv(bL87%4*C=kw"  # your password
        database = 'letterboxd'

        # Create/Connect to database
        try:
            self.connection = psycopg2.connect(
                host=hostname, user=username, password=password, dbname=database)
        except:
            print("I am unable to connect to the database")
            return

        # Create cursor, used to execute commands
        self.cur = self.connection.cursor()

        # Create quotes table if none exists
        self.cur.execute("""DROP TABLE IF EXISTS users CASCADE;
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
                                year INTEGER,
                                PRIMARY KEY(id)
                            ); 
                            -- dont make key serial here, since we're using letterboxd's ids and not adding movies in their order. also movie names might not be unique

                            CREATE TABLE reviews(
                                movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
                                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                                rating INTEGER,
                                PRIMARY KEY(movie_id, user_id)
                            );""")

    def process_item(self, item, spider):
        with open("../log.txt", mode='a') as log_file:
            log_file.write("SQL FETCH %s" % item)

        if (not any(map(lambda x: x is None, item.values()))):
            self.cur.execute("""INSERT INTO movies (id, name, year) VALUES (%s, %s, %s)""", (
                item["movie_id"],
                item["name"],
                item["year"]
            ))

            self.cur.execute(
                "INSERT INTO users (name) VALUES (%s)", (item["user"]))

            self.cur.execute(
                "SELECT * FROM users WHERE name = %s", item["name"])

            result = self.cur.fetchone()

            # if (result is None):
            #     raise RuntimeError("psycopg2 not working")
            # else:
            #     with open("../log.txt", mode='a') as log_file:
            #         log_file.write("SQL FETCH %s" % result)

            # self.cur.execute("INSERT INTO reviews (movie_id, user_id, rating)")

            # Execute insert of data into database
            self.connection.commit()
        else:
            raise RuntimeError("data contained None")
        return item

    def close_spider(self, spider):

        # Close cursor & connection to database
        self.cur.close()
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
