import psycopg2

conn = psycopg2.connect(host='localhost', user='postgres',
                        password='j?NzWpZEYHqv(bL87%4*C=kw',
                        dbname='postgres', port=5432)

cursor = conn.cursor()
