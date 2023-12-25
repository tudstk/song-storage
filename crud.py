import psycopg2
import os
import uuid

from mutagen.easyid3 import EasyID3


class DatabaseSingleton:
    connection = None

    def __new__(cls):
        if cls.connection is None:
            cls.connection = super(DatabaseSingleton, cls).__new__(cls)
            try:
                cls.connection.conn = psycopg2.connect(
                    database="SongStorage", user='postgres', password='123', host='127.0.0.1', port='5432'
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
    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS song_properties (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            file_name VARCHAR(255),
            title VARCHAR(255),
            artist VARCHAR(255),
            album VARCHAR(255),
            genre VARCHAR(255),
            release_year VARCHAR(255),
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
    if not os.path.exists("Storage"):
        os.makedirs("Storage")

    try:
        file_name = os.path.basename(song_path)
        destination_path = os.path.join("Storage", file_name)

        with open(song_path, 'rb') as source, open(destination_path, 'wb') as destination:
            for chunk in iter(lambda: source.read(4096), b''):
                destination.write(chunk)

        print(f"Song '{file_name}' has been successfully added to Storage.")

        valid_metadata_keys = ['Title', 'Artist', 'Album', 'Genre',
                               'Release Year', 'Track number', 'Composer',
                               'Publisher', 'Track Length', 'Bitrate']

        for k in valid_metadata_keys:
            if k not in metadata or not metadata[k]:
                metadata[k] = 'Unknown'

        db_connection = DatabaseSingleton()
        cursor = db_connection.get_cursor()

        insert_query = """
        INSERT INTO song_properties (id, file_name, title, artist, album, genre, release_year, track_num, composer, publisher, track_length, bitrate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (
            str(uuid.uuid4()),
            file_name,
            metadata['Title'],
            metadata['Artist'],
            metadata['Album'],
            metadata['Genre'],
            metadata['Release Year'],
            metadata['Track number'],
            metadata['Composer'],
            metadata['Publisher'],
            metadata['Track Length'],
            metadata['Bitrate']
        ))

        print(f"Metadata for '{file_name}' inserted into the database")

    except FileNotFoundError:
        print("File not found. Please provide a valid file path.")
    except Exception as e:
        print(f"Error: {e}")


def Delete_song(song_id):
    try:
        db_connection = DatabaseSingleton()
        cursor = db_connection.get_cursor()

        check_query = "SELECT id FROM song_properties WHERE id = %s"
        cursor.execute(check_query, (song_id,))
        result = cursor.fetchone()

        if result:
            delete_query = "DELETE FROM song_properties WHERE id = %s"
            cursor.execute(delete_query, (song_id,))
            db_connection.get_connection().commit()

            print(f"Song deleted with id {song_id}")
        else:
            print(f"No song with id {song_id}")

    except Exception as e:
        print(f"Error in delete_song: {e}")
        raise


def Modify_data(song_id, metadata):
    try:
        valid_metadata_keys = ['Title', 'Artist', 'Album', 'Genre',
                               'Release Year', 'Composer', 'Publisher']

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
                release_year = COALESCE(%s, release_year),
                composer = COALESCE(%s, composer),
                publisher = COALESCE(%s, publisher)
            WHERE id = %s
            """

            cursor.execute(update_query, (
                metadata.get('Title', existing_metadata[2]),
                metadata.get('Artist', existing_metadata[3]),
                metadata.get('Album', existing_metadata[4]),
                metadata.get('Genre', existing_metadata[5]),
                metadata.get('Release Year', existing_metadata[6]),
                metadata.get('Composer', existing_metadata[8]),
                metadata.get('Publisher', existing_metadata[9]),
                song_id
            ))

            print(f"Metadata updated for song with id {song_id}")

            song_path_query = "SELECT file_name FROM song_properties WHERE id = %s"
            cursor.execute(song_path_query, (song_id,))
            song_path = os.path.join("Storage", cursor.fetchone()[0])

            audio = EasyID3(song_path)
            for key, value in metadata.items():
                if key in audio:
                    audio[key] = value
            audio.save()

            print(f"Song metadata updated for song with id {song_id}")
        else:
            print(f"No song with id {song_id} found")

    except Exception as e:
        print(f"Error in Update_song: {e}")
        raise





