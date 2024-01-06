import psycopg2
import os
import uuid
import utils


class DatabaseSingleton:
    """
    A singleton class to manage the database connection.
    """

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
    """Create the "song_properties" table if it doesn't exist."""
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
        print("Success: created song properties table!")
    except psycopg2.Error as e:
        print("Error in create_song_properties_table:", e)


def Add_song(song_path, metadata):
    """Adds a song file to storage and its metadata to the database and returns the id of the added song.

        Args:
        song_path (str) -- the file path of the song.
        metadata (dict) -- a dictionary containing song metadata tags and values
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

        # add the metadata in the database
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

        # add the file to the storage
        with open(song_path, 'rb') as source, open(destination_path, 'wb') as destination:
            for chunk in iter(lambda: source.read(4096), b''):
                destination.write(chunk)

        print(f"'{file_name}' was inserted into the database with id and added to the storage.\n\n")
        return song_id
    except FileNotFoundError:
        print("File not found. Provide a valid file path.")
    except Exception as e:
        print(f"Error: {e}")


def Delete_song(song_id):
    """Deletes a song from storage and the corresponding entry in database.

       Args:
       song_id (str) -- the id of the song from the database.
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
            print(f"Success: song deleted with id {song_id}")
        else:
            print(f"No song with id {song_id}")

    except Exception as e:
        print(f"Error in delete_song: {e}")
        raise


def Modify_data(song_id, metadata):
    """Modifies the metadata of a song in the database, and if it's a '.mp3', it also modifies the file metadata.

        Args:
        song_id (str) -- the id of the song whose metadata will be modified.
        metadata (dict) -- a dictionary containing the tags and the desired values that the user wants to be updated.

        """
    try:
        valid_metadata_keys = ['Title', 'Artist', 'Album', 'Genre',
                               'Release Date', 'Track number', 'Composer',
                               'Publisher', 'Track Length', 'Bitrate']
        # check if user has provided invalid tags
        invalid_keys = [key for key in metadata.keys() if key not in valid_metadata_keys]
        if invalid_keys:
            print(f"Error: invalid metadata arguments: {invalid_keys}")
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

            # update the file metadata if the song is of mp3 type
            extension = os.path.splitext(song_path)[1]
            if extension == ".mp3":
                for tag in ['Title', 'Artist', 'Album', 'Track number', 'Release Date']:
                    if tag in metadata and metadata[tag] is not None:
                        utils.modify_id3_metadata(song_path, tag, metadata[tag])

            print(f"Success: song metadata updated for song with id {song_id}")
        else:
            print(f"Error in Modify_data: No song with id {song_id} found")

    except Exception as e:
        print(f"Error in Modify_data: {e}")
        raise
