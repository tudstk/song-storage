import datetime
import re


def clean_metadata(metadata):
    """ Removes unnecessary (0x00) and (0x03) characters from metadata values.

        Args:
        metadata (dict): Dictionary containing metadata dictionary

        Returns:
        dict: Cleaned metadata dictionary.
        """
    cleaned_metadata = {}
    for key, value in metadata.items():
        cleaned_value = value.strip('\x00\x03')
        cleaned_metadata[key] = cleaned_value
    return cleaned_metadata


def read_id3_metadata(file_path):
    """Read ID3 (v2) metadata from an audio file.

        Reads 128 bytes (file header for tags) of ID3 metadata from the beginning of an audio file,
        extracts specific frame IDs if present, and stores the metadata if user didn't provide any.This is done by
        reading ID3 tag frames (4 bytes representing the frame identifier, 4 bytes representing the size,
        followed the actual content).

        Args:
        file_path (str): Path to the song.

        Returns:
        dict: Extracted ID3 metadata dictionary.
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

        i = 10
        j = i + 10
        while j < 128:
            frame_id = id3_data[i:i + 4]
            frame_size = int.from_bytes(id3_data[i + 4:i + 8])
            if frame_id in frame_ids:
                frame_name = frame_ids[frame_id]
                frame_content = id3_data[j:j + frame_size].decode('utf-8')
                metadata[frame_name] = frame_content
            i += 10 + frame_size
            j = i + 10

    return clean_metadata(metadata)


def transform_to_snake_case(text):
    """Convert a text string to snake_case.

        Replaces spaces with underscores ensuring all characters are in lowercase. This is helpful to convert
        input identifiers (e.g. Release date) to database columns (release_date).

        Args:
        text (str): The text string to be converted.

        Returns:
        str: The text string converted to snake_case.
        """
    return '_'.join(text.lower().split())


def validate_input(field):
    """Validate user input based on the specified field.

       Asks the user for input, validates that it's empty, and
       for specific fields like 'Release Date', 'Track number', and 'Track Length',
       it performs additional validation through specialized functions.

       Args:
       field (str): The field for which the input is being validated.

       Returns:
       str or None: The validated user input or None if the input is invalid or empty.
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
    """Validate and format a date string based on accepted formats.

       Validates the provided date string by checking if they belong to some specific formats
       ("dd-mm-YYYY", "mn-YYYY", "YYYY") and returns a formatted date string if it matches
       any of the those. If the input date is None or doesn't match any accepted
       format, it returns None.

       Args:
       date (str): The date string to be validated.

       Returns:
       str or None: The formatted date string if valid, or None if the input is invalid.
       """

    if date is None:
        return None
    date_formats = ["%d-%m-%Y", "%m-%Y", "%Y"]
    for fmt in date_formats:
        try:
            if len(date) != len(datetime.datetime.strptime(date, fmt).strftime(fmt)):
                continue
            return datetime.datetime.strptime(date, fmt).strftime(fmt)
        except ValueError as e:
            print(f"date format error: {e}")
            return


def validate_track_number(track_number):
    """Validate the track number and ensure it falls within a specified range.

        Validates the provided track number by trying to convert it to an integer.
        If it's a valid integer in the range 1 - 30 (inclusive), it returns the
        track number as a string. If the input is None or not a valid integer or
        is not in the specific range, it returns None.

        Args:
        track_number (str): The track number to be validated.

        Returns:
        str or None: The validated track number as a string or None if invalid.
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
    """Validates the format of a track length in the 'mm:ss' (minutes:seconds) format.

       Args:
       track_length (str or None): A string representing the track length in 'mm:ss' format.
                                   If None, it represents unknown track length.

       Returns:
       str or None: Returns the validated track length if it matches the expected format.
                    If the input is None or doesn't match the 'mm:ss' pattern, returns None.
       """
    if track_length is None:
        return None

    pattern = re.compile(r'^([0-5][0-9]):([0-5][0-9])$')
    if pattern.match(track_length):
        return track_length
    return None


def get_mapped_inputs():
    """Gets and validates user inputs for main metadata and tags.

       This function collects user inputs for main metadata (Title, Artist, Album, Release Date, Track number)
       and tags (Genre, Composer, Publisher, Track Length, Bitrate). Dates, track numbers, and track lengths
       are validated specifically to match their expected formats.

       Returns:
       dict: A dictionary containing validated user inputs for main metadata and tags.
       """
    print("\nMAIN METADATA:\n")
    main_metadata = ['Title', 'Artist', 'Album', 'Release Date', 'Track number']
    main_inputs = {field: validate_input(field) for field in main_metadata}

    main_inputs['Release Date'] = validate_date(main_inputs['Release Date'])
    main_inputs['Track number'] = validate_track_number(main_inputs['Track number'])

    print("\nTAGS:\n")
    tags = ['Genre', 'Composer', 'Publisher', 'Track Length', 'Bitrate']
    tags = {field: validate_input(field) for field in tags}

    tags['Track Length'] = validate_track_length(tags['Track Length'])

    user_input = main_inputs.copy()
    user_input.update(tags)

    return user_input


def modify_id3_metadata(file_path, tag, new_value):
    """Modify a specific ID3 (v2) metadata tag in an audio file.

    Modifies a specific frame ID with a new value provided and includes an ETX character before the content (to mark
    the end of a previous content).

    Args: file_path (str): Path to the song. new_value (str): New value to update in the specified tag. tag (str):
    Tag identifier for the metadata field to modify (e.g., 'Title', 'Artist', 'Release Date', 'Track number', 'Album').

    Returns:
    bool: True if metadata was successfully modified, False otherwise.
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
                frame_id = id3_data[i:i + 4]
                frame_size = int.from_bytes(id3_data[i + 4:i + 8])
                if frame_id in frame_ids.values():
                    if tag in frame_ids.keys() and frame_ids[tag] == frame_id:
                        new_value = '\x03' + new_value
                        new_value = new_value.encode('utf-8')
                        if len(new_value) > frame_size:
                            frame_size = len(new_value)
                            file.seek(i + 4)
                            file.write(frame_size.to_bytes(4))
                        file.seek(j)
                        file.write(new_value.ljust(frame_size, b'\x00'))
                        return True
                i += 10 + frame_size
                j = i + 10

    return False

