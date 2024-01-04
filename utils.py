def remove_nonprintable(text):
    return ''.join(filter(lambda x: x.isprintable(), text))


def extract_frame_data(id3_data, start_index):
    frame_size = int.from_bytes(id3_data[start_index + 4:start_index + 8], byteorder='big')
    frame_content = id3_data[start_index + 10:start_index + 10 + frame_size].decode('utf-8', errors='ignore')
    return remove_nonprintable(frame_content)


def read_id3_metadata(file_path):
    metadata = {}

    with open(file_path, 'rb') as file:
        id3_data = file.read(128)

    if id3_data[:3] == b'ID3':
        size_bytes = id3_data[6:10]

        size = 0
        for i, byte in enumerate(size_bytes):
            byte_value = int(byte)
            seven_bits = byte_value % 128
            shifted_bits = seven_bits << (7 * (3 - i))
            size += shifted_bits

        frame_identifiers = {
            b'TIT2': 'Title',
            b'TPE1': 'Artist',
            b'TYER': 'Release Date',
            b'TRCK': 'Track number',
            b'TALB': 'Album'
        }

        index = 10
        while index + 10 < size:
            frame_id = id3_data[index:index + 4]
            if frame_id in frame_identifiers:
                frame_name = frame_identifiers[frame_id]
                metadata[frame_name] = extract_frame_data(id3_data, index)
            index += 10 + int.from_bytes(id3_data[index + 4:index + 8], byteorder='big')

    else:
        metadata['Error'] = "No ID3 tag found."

    return metadata


def transform_to_snake_case(text):
    return '_'.join(text.lower().split())


def nullify_input(field_name):
    user_input = input(f"{field_name}: ")
    return None if user_input == '' else user_input


def get_mapped_inputs():
    fields = ['Title', 'Artist', 'Album', 'Genre', 'Release Date', 'Track number',
              'Composer', 'Publisher', 'Track Length', 'Bitrate']

    user_input = {field: nullify_input(field) for field in fields}

    return user_input
