import psycopg

def print_user(user):
    config = {
        "host": "localhost",
        "port": "5432",
        "dbname": "postgres",
        "user": "postgres",
        "password": "Postobon12.1"
    }

    with psycopg.connect(**config) as connection:
        with connection.cursor() as cursor:
            query = "SELECT * FROM users WHERE username = %s;"
            cursor.execute(query, (user,))
            result = cursor.fetchall()

            for row in result:
                print(row)

print_user("Sebastian")