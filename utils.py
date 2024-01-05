import datetime
import re


def clean_metadata(metadata):
    cleaned_metadata = {}
    for key, value in metadata.items():
        cleaned_value = value.strip('\x00\x03')
        cleaned_metadata[key] = cleaned_value
    return cleaned_metadata


def read_id3_metadata(file_path):
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
    return '_'.join(text.lower().split())


def validate_input(field):
    while True:
        user_input = input(f"Enter {field}: ").strip()
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
    if track_length is None:
        return None

    pattern = re.compile(r'^([0-5][0-9]):([0-5][0-9])$')
    if pattern.match(track_length):
        return track_length
    return None


def get_mapped_inputs():
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
