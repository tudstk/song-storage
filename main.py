from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from math import floor
import crud


def seconds_to_minutes(audio_tag_length):
    audio_tag_length = int(round(float(audio_tag_length)))
    minutes = floor(audio_tag_length / 60)
    seconds = audio_tag_length - minutes * 60

    return f'{minutes:02d}:{seconds:02d}'


def get_song_metadata(file_path):
    try:
        audio = EasyID3(file_path)
        title, album, artist, genre, composer, publisher = (audio.get(key, [''])[0] for key in
                                                            ['title', 'album', 'artist', 'genre', 'composer',
                                                             'publisher'])
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
    dbconnection = crud.DatabaseSingleton()
    conn = dbconnection.get_connection()
    cursor = dbconnection.get_cursor()
    crud.create_song_properties_table(cursor)

    test_metadata = get_song_metadata("C:/Users/tudor/Downloads/FloatingPoint.mp3")
    if test_metadata:
        print("song metadata:")
        for key, value in test_metadata.items():
            print(f"{key}: {value}")
    else:
        print("Failed to retrieve metadata.")

    crud.Add_song("C:/Users/tudor/Downloads/FloatingPoint.mp3", test_metadata)

    crud.Delete_song("c97a3dba-120f-482d-9ab6-46e2dbf67236")

    update_metadata = {
        'Title': 'Un titlu schimbat!!?!',
        'Artist': 'Un artist schimbat!!?',
        'Publisher': 'Cineva?!'
    }
    crud.Modify_data("1acddf15-6d81-4d96-a00c-c719bf8fae71", update_metadata)

    conn.commit()
    conn.close()
