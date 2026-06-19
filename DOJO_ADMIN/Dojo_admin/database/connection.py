import psycopg
from psycopg_pool import ConnectionPool

class Database:

    def __init__(self):
        self.pool = ConnectionPool(
            conninfo="host=localhost port=5432 dbname=postgres user=postgres password=Postobon12.1",
            min_size=1,
            max_size=10
        )

    def get_conn(self):
        return self.pool.getconn()

    def release(self, conn):
        self.pool.putconn(conn)

db = Database()