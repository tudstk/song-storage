import psycopg2
from crud import DatabaseSingleton


def Search(criteria):
    try:
        db_connection = DatabaseSingleton()
        cursor = db_connection.get_cursor()

        search_query = ("SELECT file_name, title, artist, album, genre, release_year, track_num, composer, "
                        "publisher, track_length, bitrate FROM song_properties WHERE ")
        conditions = []

        for key, value in criteria.items():
            conditions.append(f"{key.lower()} ILIKE %s")
            cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'song_properties' AND "
                "column_name = %s",
                (key.lower(),))

            column_exists = cursor.fetchone()
            if not column_exists:
                print(f"Column '{key}' does not exist in the database.")
                return None

        search_query += " AND ".join(conditions)

        criteria_values = [v.lower() if isinstance(v, str) else v for v in criteria.values()]
        cursor.execute(search_query, tuple(criteria_values))

        songs_found = cursor.fetchall()

        if songs_found:
            print("Matching songs found:")
            columns = [desc[0] for desc in cursor.description]
            for song in songs_found:
                filtered_song = {columns[i]: value for i, value in enumerate(song) if value != 'Unknown'}
                for key, value in filtered_song.items():
                    print(f"'{key}' = '{value}'")
                print("\n")
        else:
            print("No songs found for your search filters.")

    except psycopg2.Error as e:
        print(f"Error in Search: {e}")
        raise
