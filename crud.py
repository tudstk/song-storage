import psycopg2
import os
import uuid
import utils


class DatabaseSingleton:
    connection = None

    def __new__(cls):
        if cls.connection is None:
            cls.connection = super(DatabaseSingleton, cls).__new__(cls)
            try:
                cls.connection.conn = psycopg2.connect(
                    database="SongStorage", user='postgres', password='1234', host='127.0.0.1', port='5432'
                )
                cls.connection.cursor = cls.connection.conn.cursor()
                cls.connection.cursor.execute("select version()")
                data = cls.connection.cursor.fetchone()
                print("Connection established to: ", data)
            except psycopg2.Error as e:
                print("Error while connecting to db:", e)
        return cls.connection

    def get_connection(self):
        return self.conn

    def get_cursor(self):
        return self.cursor

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
        print("Connection closed.")


def create_song_properties_table(cursor):
    """Creates the 'song_properties' table if it does not exist.

        This function attempts to create the 'song_properties' table in the database with the specified columns.
        If the table already exists, it won't be recreated.

        Args:
        cursor: Database cursor object used to execute SQL queries.

        Returns:
        None
        """
    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS song_properties (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            file_name VARCHAR(255),
            title VARCHAR(255),
            artist VARCHAR(255),
            album VARCHAR(255),
            genre VARCHAR(255),
            release_date VARCHAR(255),
            track_num VARCHAR(255),
            composer VARCHAR(255),
            publisher VARCHAR(255),
            track_length VARCHAR(255),
            bitrate VARCHAR(255)
        );
        """
        cursor.execute(create_table_query)
        print("Successfully created song properties table!")
    except psycopg2.Error as e:
        print("Error while creating properties table:", e)


def Add_song(song_path, metadata):
    """Adds a song file to storage and its metadata to the database.

        Creates a 'Storage' directory if it doesn't exist and saves the song file there.
        Validates and check what metadata fields were completed by the user in the provided metadata. The metadata
        that wasn't filled, will be marked as Unknown in the database.
        Inserts the song metadata into the 'song_properties' table in the database.

        Args:
        song_path (str): The file path of the song.
        metadata (dict): A dictionary containing song metadata with keys for 'Title', 'Artist', 'Album', 'Genre',
                         'Release Date', 'Track number', 'Composer', 'Publisher', 'Track Length', and 'Bitrate'.

        Returns:
        None
        """
    if not os.path.exists("Storage"):
        os.makedirs("Storage")

    try:
        print("RECEIVED METADATAAA:", metadata)
        file_name = os.path.basename(song_path)
        destination_path = os.path.join("Storage", file_name)

        valid_metadata_keys = ['Title', 'Artist', 'Album', 'Genre',
                               'Release Date', 'Track number', 'Composer',
                               'Publisher', 'Track Length', 'Bitrate']

        for k in valid_metadata_keys:
            if k not in metadata or not metadata[k]:
                metadata[k] = 'Unknown'
            else:
                print(metadata[k])

        db_connection = DatabaseSingleton()
        cursor = db_connection.get_cursor()

        insert_query = """
        INSERT INTO song_properties (id, file_name, title, artist, album, genre, release_date, track_num, composer, publisher, track_length, bitrate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        song_id = str(uuid.uuid4())

        print("METADATA DE TITLEEEE:", metadata['Title'])
        cursor.execute(insert_query, (
            song_id,
            file_name,
            metadata['Title'],
            metadata['Artist'],
            metadata['Album'],
            metadata['Genre'],
            metadata['Release Date'],
            metadata['Track number'],
            metadata['Composer'],
            metadata['Publisher'],
            metadata['Track Length'],
            metadata['Bitrate']
        ))

        with open(song_path, 'rb') as source, open(destination_path, 'wb') as destination:
            for chunk in iter(lambda: source.read(4096), b''):
                destination.write(chunk)

        print(f"'{file_name}' was inserted into the database with id {song_id}, and was added to the storage.\n\n")

    except FileNotFoundError:
        print("File not found. Please provide a valid file path.")
    except Exception as e:
        print(f"Error: {e}")


def Delete_song(song_id):
    """Deletes a song from the database and its associated file from storage.

       This function takes a song ID as input and checks the 'song_properties' table in the database for the song with
        the provided ID. If the song exists, it deletes the entry from the table and removes the associated file
        from the 'Storage' directory.
        If no song is found with the provided ID, it prints an error message.

       Args:
       song_id (str): The unique identifier of the song to be deleted.

       Returns:
       None
       """
    try:
        db_connection = DatabaseSingleton()
        cursor = db_connection.get_cursor()

        check_query = "SELECT id, file_name FROM song_properties WHERE id = %s"
        cursor.execute(check_query, (song_id,))
        result = cursor.fetchone()

        if result:
            delete_query = "DELETE FROM song_properties WHERE id = %s"
            cursor.execute(delete_query, (song_id,))
            db_connection.get_connection().commit()
            os.remove("Storage/" + result[1])
            print(f"Song deleted with id {song_id}")
        else:
            print(f"No song with id {song_id}")

    except Exception as e:
        print(f"Error in delete_song: {e}")
        raise


def Modify_data(song_id, metadata):
    """Modifies metadata for a song entry in the database and associated file.

        Updates metadata for a song in the database and file properties, corresponding to the provided song ID.

        Retrieves existing metadata from the database for the given song ID.Updates the corresponding metadata
        fields in the database based on the provided metadata. Utilizes 'modify_id3_metadata' to update ID3
        tags in the associated song file, if applicable.

        Args:
        song_id (str): The id of the song whose metadata will be modified.
        metadata (dict): A dictionary containing updated metadata for the song.

        """
    try:
        valid_metadata_keys = ['Title', 'Artist', 'Album', 'Genre',
                               'Release Date', 'Track number', 'Composer',
                               'Publisher', 'Track Length', 'Bitrate']

        invalid_keys = [key for key in metadata.keys() if key not in valid_metadata_keys]
        if invalid_keys:
            print(f"Invalid metadata arguments: {invalid_keys}")
            return

        db_connection = DatabaseSingleton()
        cursor = db_connection.get_cursor()

        check_query = "SELECT * FROM song_properties WHERE id = %s"
        cursor.execute(check_query, (song_id,))
        existing_metadata = cursor.fetchone()

        if existing_metadata:
            update_query = """
            UPDATE song_properties
            SET title = COALESCE(%s, title),
                artist = COALESCE(%s, artist),
                album = COALESCE(%s, album),
                genre = COALESCE(%s, genre),
                release_date = COALESCE(%s, release_date),
                track_num = COALESCE(%s, track_num),
                composer = COALESCE(%s, composer),
                publisher = COALESCE(%s, publisher),
                track_length = COALESCE(%s, track_length),
                bitrate = COALESCE(%s, bitrate)

            WHERE id = %s
            """

            cursor.execute(update_query, (
                metadata.get('Title', existing_metadata[2]),
                metadata.get('Artist', existing_metadata[3]),
                metadata.get('Album', existing_metadata[4]),
                metadata.get('Genre', existing_metadata[5]),
                metadata.get('Release Date', existing_metadata[6]),
                metadata.get('Track number', existing_metadata[7]),
                metadata.get('Composer', existing_metadata[8]),
                metadata.get('Publisher', existing_metadata[9]),
                metadata.get('Track Length', existing_metadata[10]),
                metadata.get('Bitrate', existing_metadata[11]),
                song_id
            ))

            song_path_query = "SELECT file_name FROM song_properties WHERE id = %s"
            cursor.execute(song_path_query, (song_id,))

            song_path = os.path.join("Storage", cursor.fetchone()[0])

            for tag in ['Title', 'Artist', 'Album', 'Track number', 'Release Date']:
                if tag in metadata and metadata[tag] is not None:
                    utils.modify_id3_metadata(song_path, tag, metadata[tag])

            print(f"Song metadata updated for song with id {song_id}")
        else:
            print(f"No song with id {song_id} found")

    except Exception as e:
        print(f"Error in Update_song: {e}")
        raise
