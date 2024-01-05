import psycopg2
import zipfile
import utils
from crud import DatabaseSingleton


def Search(filters):
    """Searches for songs in the database based on given filters.

        This function searches in the 'song_properties' table of the database using the given filters.
        It constructs a SQL query based on the provided filters and retrieves songs that match user's search filters.

        Args:
        filters (dict): A dictionary containing filters for searching song properties.

        Returns:
        list or None: A list of songs found in the database that match the provided filters, or None if no matches
         are found.
        """
    try:
        db_connection = DatabaseSingleton()
        cursor = db_connection.get_cursor()

        search_query = ("SELECT file_name, title, artist, album, genre, release_date, track_num, composer, "
                        "publisher, track_length, bitrate FROM song_properties WHERE ")
        conditions = []

        filters = {key: value for key, value in filters.items() if value is not None}

        for key, value in filters.items():
            conditions.append(f"{utils.transform_to_snake_case(key)} ILIKE %s")
            cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'song_properties' AND "
                "column_name = %s",
                (utils.transform_to_snake_case(key),))

            column_exists = cursor.fetchone()
            if not column_exists:
                print(f"Column '{key}' does not exist in the database.")
                return None

        search_query += " AND ".join(conditions)

        filters_values = [v for v in filters.values()]

        print('FILTERS VALUES', filters_values)
        cursor.execute(search_query, tuple(filters_values))

        songs_found = cursor.fetchall()

        print("SONGS FOUND", songs_found)

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
    """Creates and saves a playlist of songs matching filters specified by user into a ZIP archive.

      This function creates a playlist by searching for songs in the database based on the provided filters
      using 'Search' function.
      It then generates a ZIP archive containing the found songs and saves it to the specified output folder.

      Args:
      output_folder (str): The directory path where the playlist ZIP archive will be saved.
      filters (dict): A dictionary containing filters for searching song properties.
      """
    try:
        songs_found = Search(filters)

        if songs_found:

            with zipfile.ZipFile(output_folder + "/playlist.zip", 'w') as zip_file:
                for song in songs_found:
                    file_name = song[0]
                    source_path = 'Storage/' + file_name

                    try:
                        zip_file.write(source_path, arcname=file_name)
                        print(f"File added to the archive.")
                    except FileNotFoundError:
                        print(f"File not found.")

            print("Archive created!")
        else:
            print("No songs found for your search filters.")

    except Exception as e:
        print(f"Error in Create_save_list: {e}")
