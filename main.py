from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from math import floor
import crud
import filtering


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
        year = audio.get('date', [''])[0].split('-')[0]

        audio_tags = MP3(file_path)
        track_number = str(audio_tags.tags.get('TRCK', [''])[0])
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


if __name__ == '__main__':
    dbconnection = crud.DatabaseSingleton()
    conn = dbconnection.get_connection()
    cursor = dbconnection.get_cursor()
    crud.create_song_properties_table(cursor)

    song_path = 'C:/Users/tudor/Downloads/Vertigo Queen.mp3'

    metadata1 = get_song_metadata(song_path)
    # crud.Add_song(song_path, metadata1)

    # crud.Delete_song("2c6f1225-353b-41e7-857e-44a5c9bc8b5c")

    update_metadata = {
        'Title': 'Liber',
        'Artist': 'Keo',
        'Album': 'Nu stiu',
        'Genre': 'Pop',
        'Release Year': '2011',
        'Composer': 'Keo',
        'Publisher': 'Keo',
    }
    crud.Modify_data("29f0a460-e2b7-4953-8056-e21f542a3d8b", update_metadata)

    search_dict = {
        'Artist': 'Alon mor'
    }
    filtering.Search(search_dict)

    filtering.Create_save_list('D:/pp_output', search_dict, "playlist_alanmor.zip")

    conn.commit()
    conn.close()
