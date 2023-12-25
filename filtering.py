import psycopg2
import zipfile
import os
from crud import DatabaseSingleton


def Search(filters):
    try:
        db_connection = DatabaseSingleton()
        cursor = db_connection.get_cursor()

        search_query = ("SELECT file_name, title, artist, album, genre, release_year, track_num, composer, "
                        "publisher, track_length, bitrate FROM song_properties WHERE ")
        conditions = []

        for key, value in filters.items():
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

        filters_values = [v.lower() if isinstance(v, str) else v for v in filters.values()]
        cursor.execute(search_query, tuple(filters_values))

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


def Create_save_list(output_folder, filters):
    try:
        songs_found = Search(filters)

        if songs_found:

            with zipfile.ZipFile(output_folder, 'w') as zip_file:
                for song in songs_found:
                    file_name = song[0]
                    source_path = os.path.join("Storage", file_name)

                    try:
                        zip_file.write(source_path, arcname=file_name)
                        print(f"File added to the archive.")
                    except FileNotFoundError:
                        print(f"File not found.")

            print("Zip archive created!")
        else:
            print("No songs found for your search filters.")

    except Exception as e:
        print(f"Error in Create_save_list: {e}")
