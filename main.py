import psycopg2
import os
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from math import floor


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
            id SERIAL PRIMARY KEY,
            file_name VARCHAR(255),
            title VARCHAR(255),
            artist VARCHAR(255),
            album VARCHAR(255),
            genre VARCHAR(255),
            release_year INTEGER,
            track_num INTEGER,
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


def seconds_to_minutes(audio_tag_length):
    audio_tag_length = int(round(float(audio_tag_length)))
    minutes = floor(audio_tag_length / 60)
    seconds = audio_tag_length - minutes * 60

    return f'{minutes}:{seconds}'


def get_song_metadata(file_path):
    try:
        audio = EasyID3(file_path)
        title, album, artist, genre, composer, publisher = (audio.get(key, [''])[0] for key in ['title', 'album', 'artist', 'genre', 'composer', 'publisher'])
        year = int((audio.get('date', [''])[0]).split('-')[0])

        audio_tags = MP3(file_path)
        track_number = audio_tags.tags['TRCK'][0]
        length = seconds_to_minutes(audio_tags.info.length)
        bitrate = str(floor(audio_tags.info.bitrate / 1000)) + 'kbs'

        return {
            'Title': title,
            'Artist': artist,
            'Album': album,
            'Genre': genre,
            'Release Year': year,
            'Track number': track_number,
            'Composer': composer,
            'Publisher': publisher,
            'Track Length': length,
            'Bitrate': bitrate
        }
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == '__main__':
    dbconnection = DatabaseSingleton()
    conn = dbconnection.get_connection()
    cursor = dbconnection.get_cursor()
    create_song_properties_table(cursor)
    conn.commit()
    conn.close()

    file_path = 'Storage/Ancestral.mp3'
    metadata = get_song_metadata(file_path)
    if metadata:
        print("song metadata:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
    else:
        print("Failed to retrieve metadata.")
