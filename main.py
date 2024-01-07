import os
import crud
import filtering
import utils


def display_menu():
    """Displays the main menu of functionalities for SongStorage and returns a string which represents the user's
    choice"""
    print("Welcome to SongStorage!")
    print("These are the available functionalities:")
    print("--*-- 1 --*--. Add Song (song path, metadata)")
    print("--*-- 2 --*--. Delete Song (song ID)")
    print("--*-- 3 --*--. Modify data (song ID, new metadata")
    print("--*-- 4 --*--. Search (filters)")
    print("--*-- 5 --*--. Create Save List (output path, filters)")
    print("--*-- 6 --*--. Play (song name from storage)")
    print("--*-- 7 --*--. Exit")
    return input("Please enter your choice (1-7): ")


def add_song():
    """Add a song to the database and Storage by calling Add_song function from the 'crud' file."""
    valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.aff']
    song_path = input("Enter the path of the song file: ")
    if not os.path.exists(song_path):
        print("File does not exist.")
        return

    file_extension = os.path.splitext(song_path)[1]
    if file_extension not in valid_extensions:
        print(f'Invalid audio file format. Supported formats: {valid_extensions}')
        return

    print("Please enter the following metadata for the song:")

    user_input = utils.get_mapped_inputs()

    # if the file is a mp3 then the tags that are not provided by the user will be filled from the file metadata
    if song_path.split('.')[1] == 'mp3':
        song_metadata = utils.read_id3_metadata(song_path)
        attributes_to_check = ['Title', 'Artist', 'Release Date', 'Track number', 'Album']

        for attribute in attributes_to_check:
            if attribute in user_input and attribute in song_metadata:
                user_input[attribute] = user_input[attribute] or song_metadata[attribute]

        for key, value in song_metadata.items():
            if key not in user_input:
                user_input[key] = value

    print("User input:", user_input)
    song_id = crud.Add_song(song_path, user_input)
    print(f'Song added with id: {song_id}')


def delete_song():
    """Delete a song from the database and Storage by calling Delete_song function from the 'crud' file."""
    song_id = input("Enter Song ID: ")
    crud.Delete_song(song_id)


def modify_data():
    """Update a song from the database and Storage by calling the Modify_data function from the 'crud' file."""
    song_id = input("Enter Song ID: ")

    print("Metadata to change:")
    user_input = utils.get_mapped_inputs()

    crud.Modify_data(song_id, user_input)


def search():
    """Search for songs in the database based on filters specified by user by using Search function
    from 'filtering' file """

    user_input = utils.get_mapped_inputs_filters()
    filtering.Search(user_input)


def create_savelist():
    """Create a savelist of songs based on specified filters by using Create_savelist function from 'filtering' file """
    output_path = input("Enter the output path for the savelist: ")
    user_input = utils.get_mapped_inputs_filters()

    filtering.Create_save_list(output_path, user_input)


def play():
    """Play a selected song from the storage."""
    song_name = input("Enter the name of the song: ")

    current_path = os.path.dirname(os.path.abspath(__file__))
    song_path = current_path + '/Storage/' + song_name

    if not os.path.exists(song_path):
        print(f"'{song_name}' not found in Storage")
        return

    try:
        os.startfile(song_path)
    except OSError as e:
        print(f"Error in Play: {e}")


if __name__ == '__main__':
    """The entry point of the application."""

    dbconnection = crud.DatabaseSingleton()
    conn = dbconnection.get_connection()
    cursor = conn.cursor()
    crud.create_song_properties_table(cursor)

    while True:
        choice = display_menu()

        if choice == '1':
            add_song()
            conn.commit()
        elif choice == '2':
            delete_song()
            conn.commit()
        elif choice == '3':
            modify_data()
            conn.commit()
        elif choice == '4':
            search()
            conn.commit()
        elif choice == '5':
            create_savelist()
            conn.commit()
        elif choice == '6':
            play()
        elif choice == '7':
            print("Goodbye!")
            conn.close()
            break
        else:
            print("Enter a number between 1 and 7.")
