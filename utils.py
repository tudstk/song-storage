import datetime
import re


def clean_metadata(metadata):
    """ Removes unnecessary (0x00) and (0x03) characters from metadata values and returns the clean metadata.

    Args:
    metadata (dict) -- dictionary containing metadata with useless characters.
    """
    cleaned_metadata = {}
    for key, value in metadata.items():
        cleaned_value = value.strip('\x00\x03')
        cleaned_metadata[key] = cleaned_value
    return cleaned_metadata


def read_id3_metadata(file_path):
    """Read ID3 (v2) metadata from an audio file and returns the extracted metadata from file

    Args:
    file_path (str) -- path to the song.
    """

    metadata = {}

    with open(file_path, 'rb') as file:
        id3_data = file.read(128)

    if id3_data.startswith(b'ID3'):
        frame_ids = {
            b'TIT2': 'Title',
            b'TPE1': 'Artist',
            b'TYER': 'Release Date',
            b'TRCK': 'Track number',
            b'TALB': 'Album'
        }
        # a frame has 10 bytez
        i = 10
        j = i + 10

        # tags are placed in the first 128 bytes of the file
        while j < 128:
            frame_id = id3_data[i:i + 4]
            # first 4 bytes of a frame store the tag and the next 4 store the size of the actual content
            frame_size = int.from_bytes(id3_data[i + 4:i + 8])
            if frame_id in frame_ids:
                frame_name = frame_ids[frame_id]
                # so after getting the size, I have to read that specific number of bytes to get the content
                frame_content = id3_data[j:j + frame_size].decode('utf-8')
                metadata[frame_name] = frame_content
            i += 10 + frame_size
            j = i + 10

    return clean_metadata(metadata)


def transform_to_snake_case(text):
    """Convert a text string to snake_case and returns it

    Args:
    text (str): The text string to be converted.
    """
    return '_'.join(text.lower().split())


def validate_input(field):
    """Validate user input based on the specified field and return the validated input if the user has provided
    the specific input, else return none.

    Args:
    field (str): The field for which the input is being validated.
    """
    while True:
        user_input = input(f"{field}: ").strip()
        if not user_input:
            return None
        if field == 'Release Date':
            validated_input = validate_date(user_input)
        elif field == 'Track number':
            validated_input = validate_track_number(user_input)
        elif field == 'Track Length':
            validated_input = validate_track_length(user_input)
        else:
            validated_input = user_input
        if validated_input is not None:
            return validated_input
        else:
            print(f"Invalid input for {field}. Try again")


def validate_date(date):
    """Checks if date input is valid and returns the formatted date string if it's valid, else it returns None.

    Args:
    date (str): The date string to be validated.
    """

    if date is None:
        return None
    date_formats = ["%d-%m-%Y", "%m-%Y", "%Y"]
    for fmt in date_formats:
        try:
            if len(date) != len(datetime.datetime.strptime(date, fmt).strftime(fmt)):
                continue
            # formats the string as a date object then converts it to a string again
            return datetime.datetime.strptime(date, fmt).strftime(fmt)
        except ValueError as e:
            print(f"date format error: {e}")
            return


def validate_track_number(track_number):
    """Validate the track number and ensure it is between the range (1, 30) and returns the track number as a string
    if the validation succeeded, else it returns none.

    Args:
    track_number (str) -- The track number to be validated.
    """
    if track_number is None:
        return None

    try:
        track_number = int(track_number)
        if 1 <= track_number <= 30:
            return str(track_number)
    except ValueError as e:
        print(f"Track number is not a number: {e}")
        return


def validate_track_length(track_length):
    """Validates the format of a track length in the (minutes:seconds) format, and it returns it if it matches the
    pattern, else it returns none.

    Args:
    track_length (str or None) -- A string representing the track length.
                                If None, it means that the track length will be marked as Unknown.
    """
    if track_length is None:
        return None

    # matches the (minutes:seconds) pattern where the max is 59 and 59 for each one
    pattern = re.compile(r'^([0-5][0-9]):([0-5][0-9])$')
    if pattern.match(track_length):
        return track_length
    return None


def get_mapped_inputs():
    """Gets user inputs for main metadata then returns the input after validation."""
    print("\nMAIN METADATA:\n")
    main_metadata = ['Title', 'Artist', 'Album', 'Release Date', 'Track number']
    main_inputs = {field: validate_input(field) for field in main_metadata}

    main_inputs['Release Date'] = validate_date(main_inputs['Release Date'])
    main_inputs['Track number'] = validate_track_number(main_inputs['Track number'])

    print("\nTAGS:\n")
    tags = ['Genre', 'Composer', 'Publisher', 'Track Length']
    tags = {field: validate_input(field) for field in tags}

    tags['Track Length'] = validate_track_length(tags['Track Length'])

    user_input = main_inputs.copy()
    user_input.update(tags)

    return user_input


def get_mapped_inputs_filters():
    """Gets user inputs for main metadata then returns the input after validation."""

    print("Fill the filters you want:")
    main_metadata_filters = ['Title', 'Artist', 'Album']
    main_inputs_filters = {field: validate_input(field) for field in main_metadata_filters}

    tags = ['Genre', 'Composer', 'Publisher', 'File Format']
    tags = {field: validate_input(field) for field in tags}

    user_input = main_inputs_filters.copy()
    user_input.update(tags)

    return user_input


def modify_id3_metadata(file_path, tag, new_value):
    """Modify a specific ID3 metadata tag in an audio file and returns True if the metadata was modified,
    False otherwise.

    Args:
    file_path (str) -- path to the song.
    tag (str) -- the tag name (e.g. 'Artist', 'Genre', etc.)
    new_value (str) -- new value to update in the specified tag
    """

    frame_ids = {
        'Title': b'TIT2',
        'Artist': b'TPE1',
        'Release Date': b'TYER',
        'Track number': b'TRCK',
        'Album': b'TALB'
    }

    with open(file_path, 'r+b') as file:
        id3_data = file.read(128)

        if id3_data.startswith(b'ID3'):
            i = 10
            j = i + 10
            while j < 128:
                # getting the tag name
                frame_id = id3_data[i:i + 4]
                # getting the tag size
                frame_size = int.from_bytes(id3_data[i + 4:i + 8])
                if frame_id in frame_ids.values():
                    # if the specified tag was found, add an RTE character to mark the end of the previous frame
                    if tag in frame_ids.keys() and frame_ids[tag] == frame_id:
                        new_value = '\x03' + new_value
                        new_value = new_value.encode('utf-8')
                        # the tag value that I insert may be bigger than the current one, so resizing is needed
                        if len(new_value) > frame_size:
                            frame_size = len(new_value)
                            file.seek(i + 4)
                            file.write(frame_size.to_bytes(4))
                        file.seek(j)
                        # else, if the tag value is smaller than the current one, the remaining bytes will be NULL
                        file.write(new_value.ljust(frame_size, b'\x00'))
                        return True
                i += 10 + frame_size
                j = i + 10

    return False
