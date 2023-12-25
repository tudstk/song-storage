import psycopg2
import os
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
            return songs_found
        else:
            print("No songs found for your search filters.")

    except psycopg2.Error as e:
        print(f"Error in Search: {e}")
        raise


def Create_save_list(output_folder, criteria):
    try:
        songs_found = Search(criteria)

        if songs_found:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            for song in songs_found:
                file_name = song[0]
                source_path = os.path.join("Storage", file_name)
                destination_path = os.path.join(output_folder, file_name)
                try:
                    with open(source_path, 'rb') as source, open(destination_path, 'wb') as destination:
                        while True:
                            chunk = source.read(4096)
                            if not chunk:
                                break
                            destination.write(chunk)
                    print(f"File '{source_path}' copied to '{destination_path}'")
                except FileNotFoundError:
                    print("File not found.")
    except Exception as e:
        print(f"Error in Create_save_list: {e}")
