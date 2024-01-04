import os
import crud
import filtering
import utils


def display_menu():
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
    dbconnection = crud.DatabaseSingleton()
    conn = dbconnection.get_connection()

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

    conn.commit()
    conn.close()


def delete_song():
    dbconnection = crud.DatabaseSingleton()
    conn = dbconnection.get_connection()

    song_id = input("Enter Song ID: ")
    crud.Delete_song(song_id)

    conn.commit()
    conn.close()


def modify_data():
    dbconnection = crud.DatabaseSingleton()
    conn = dbconnection.get_connection()

    song_id = input("Enter Song ID: ")

    print("Metadata to change:")
    user_input = utils.get_mapped_inputs()

    crud.Modify_data(song_id, user_input)

    conn.commit()
    conn.close()


def search():
    dbconnection = crud.DatabaseSingleton()
    conn = dbconnection.get_connection()

    print("Fill the filters you want:")

    user_input = utils.get_mapped_inputs()
    filtering.Search(user_input)

    conn.commit()
    conn.close()


def create_savelist():
    dbconnection = crud.DatabaseSingleton()
    conn = dbconnection.get_connection()

    output_path = input("Enter the output path for the savelist: ")
    user_input = utils.get_mapped_inputs()

    filtering.Create_save_list(output_path, user_input)

    conn.commit()
    conn.close()


def play():
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
    while True:
        choice = display_menu()

        if choice == '1':
            add_song()
        elif choice == '2':
            delete_song()
        elif choice == '3':
            modify_data()
        elif choice == '4':
            search()
        elif choice == '5':
            create_savelist()
        elif choice == '6':
            play()
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")
