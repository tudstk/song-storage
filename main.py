import os
import crud
import filtering
import utils


def display_menu():
    """Displays the main menu of functionalities for SongStorage.

       This function prints the available functionalities in the SongStorage application's main menu.
       It prompts the user to input their choice corresponding to each functionality.

    Returns:
    str: The user's choice representing the selected functionality (1-7).
    """
    print("Welcome to SongStorage!")
    print("These are the available functionalities:")
    print("--*-- 1 --*--. Add Song")
    print("--*-- 2 --*--. Delete Song")
    print("--*-- 3 --*--. Modify data")
    print("--*-- 4 --*--. Search")
    print("--*-- 5 --*--. Create Save List")
    print("--*-- 6 --*--. Play")
    print("--*-- 7 --*--. Exit")
    return input("Please enter your choice (1-7): ")


def add_song():
    """Add a song to the database and Storage.

    This function prompts the user to input the path of the song file and its associated metadata.
    If the file is '.mp3' then properties that are not given by the user will be extracted from the file.
    It uses the Add_song function to perform the effective operations.

    """
    song_path = input("Enter the path of the song file: ")

    print("Please enter the following metadata for the song:")

    user_input = utils.get_mapped_inputs()

    if song_path.split('.')[1] == 'mp3':
        song_metadata = utils.read_id3_metadata(song_path)
        attributes_to_check = ['Title', 'Artist', 'Release Date', 'Track number', 'Album']

        for attribute in attributes_to_check:
            if attribute in user_input and attribute in song_metadata:
                user_input[attribute] = user_input[attribute] or song_metadata[attribute]

        for key, value in song_metadata.items():
            if key not in user_input:
                user_input[key] = value

    print("USSERRR INPUTT", user_input)
    crud.Add_song(song_path, user_input)


def delete_song():
    """Delete a song from the database and Storage.

    This function prompts the user to input the ID of the song they want to delete from the database.
    It uses the Delete_song function to delete the specified song by its ID and delete the song from the Storage.
    """
    song_id = input("Enter Song ID: ")
    crud.Delete_song(song_id)


def modify_data():
    """Updates a song from the database and Storage.

    This function prompts the user to input the ID from the database. of the song they want to modify and the
    metadata to update the song.
    It uses the Modify_data function to update the song data in the database and rewrite the file if it's a '.mp3'.
    """
    song_id = input("Enter Song ID: ")

    print("Metadata to change:")
    user_input = utils.get_mapped_inputs()

    crud.Modify_data(song_id, user_input)


def search():
    """Search for songs in the database based on filters specified by user.

    This function prompts the user to input filters for searching songs in the database and uses Search function
    to do the effective operation.

    """
    print("Fill the filters you want:")

    user_input = utils.get_mapped_inputs()
    filtering.Search(user_input)


def create_savelist():
    """Create a savelist of songs based on specified filters.

       This function prompts the user to input the output path for the save list and provides filters for song selection.
       It then calls the Create_save_list function to perform the effective operation.
    """
    output_path = input("Enter the output path for the savelist: ")
    user_input = utils.get_mapped_inputs()

    filtering.Create_save_list(output_path, user_input)


def play():
    """Play a selected song from the SongStorage.

        This function prompts the user to enter the name of the song they want to play.
        It constructs the path to the song file and starts playing using the default OS player.
    """
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
    """Entry point for SongStorage application.
    
       This section initializes the database connection and presents a console menu interface
       for users to interact with the SongStorage functionalities including adding, deleting,
       modifying data, searching, creating save lists, and playing songs.
    
       The loop continues until the user chooses to exit the program. It ensures continuous
       interaction with the user, executing specific functions based on the user's choice.
    """

    dbconnection = crud.DatabaseSingleton()
    conn = dbconnection.get_connection()

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
            print("Please enter a number between 1 and 7.")
