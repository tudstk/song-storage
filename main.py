import psycopg2

def connect_to_db():
    try:
        conn = psycopg2.connect(
            database="SongStorage", user='postgres', password='123', host='127.0.0.1', port='5432'
        )
        cursor = conn.cursor()

        cursor.execute("select version()")
        data = cursor.fetchone()
        print("Connection established to: ", data)

        return conn, cursor
    except psycopg2.Error as e:
        print("Error while connecting to db:", e)


def create_song_properties_table(cursor):
    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS SongProperties (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            artist VARCHAR(255),
            album VARCHAR(255),
            track_num INTEGER,
            composer VARCHAR(255),
            publisher VARCHAR(255),
            album_artist VARCHAR(255)
        );
        """
        cursor.execute(create_table_query)
        print("Successfully created song properties table!")
    except psycopg2.Error as e:
        print("Error while creating properties table:", e)


if __name__ == '__main__':
    conn, cursor = connect_to_db()
    create_song_properties_table(cursor)
    conn.commit()
    conn.close()
