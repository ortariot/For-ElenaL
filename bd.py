import psycopg2

conn = psycopg2.connect(
    host='localhost',
    user='student',
    password='student',
    database='ElenaLebedeva'
)


def create_table_seen_person(conn):
    """создает  БД"""
    with conn.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE seen_person(
                id_vk INTEGER NOT NULL,
                id_ws INTEGER NOT NULL,
                PRIMARY KEY(id_vk, id_ws));"""
        )
        conn.commit()


def insert_data_seen_person(conn, id_vk, id_ws):
    """вставка данных в таблицуe"""
    with conn.cursor() as cursor:
        cursor.execute(
            f"""
            INSERT INTO seen_person (id_vk, id_ws)
            VALUES ({id_vk}, {id_ws})
           """
        )
        conn.commit()


def check(conn, id_vk, id_ws):
    with conn.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT id_vk FROM seen_person 
            WHERE id_vk = {id_vk} AND id_ws = {id_ws};
            """
        )
        out = cursor.fetchall()

    return False if out else True


# def delete_table_seen_person():
#     """удаляет БД"""
#     with conn.cursor() as cursor:
#         cursor.execute(
#             """DROP TABLE  IF EXISTS seen_person CASCADE;"""
#         )


if __name__ == '__main__':
    conn = psycopg2.connect(
        host='localhost',
        user='student',
        password='student',
        database='ElenaLebedeva'
    )

    create_table_seen_person(conn)
