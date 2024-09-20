import psycopg2

try:
    conn = psycopg2.connect(
        "dbname='letterboxd' user='postgres' host='localhost' password='j?NzWpZEYHqv(bL87%4*C=kw'")
    print("Connection Successful")
except:
    print("I am unable to connect to the database")
