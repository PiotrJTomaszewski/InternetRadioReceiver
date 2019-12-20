import re


def process_metadata_shoutcast(song):
    metadata = {
        'radio_address': song.get('file'),
        'radio_name': song.get('name')}
    title = song['title']
    # Check if there is an album release date at the end of the title (Release year is written in parenthesis)
    if re.match('\([0-9]{4}\)', title[-6:]):
        metadata['release_year'] = title[-6:]
        # Remove the parenthesis
        metadata['release_year'] = metadata['release_year'][1:-1]
        title = title[:-6].rstrip()
    # Split title and artist (They are usually separated by a '-' signs)
    title_splitted = title.split('-')
    if len(title_splitted) == 2:  # If there are both artist and title
        metadata['artist'] = title_splitted[0].rstrip()
        metadata['title'] = title_splitted[1].lstrip()
    elif len(title_splitted) == 1:  # Couldn't split so consider it all a title
        metadata['title'] = title
    else:
        print("Error: The title seems to have more '-' than 2? {}".format(title))
    print(title)
    return metadata


if __name__ == '__main__':
    print(process_metadata_shoutcast(
        {'file': 'http://144.217.29.205:80/live', 'title': 'Piledriver - Witch Hunt (1234)', 'name': 'HardRadio',
         'pos': '0',
         'id': '1'}))
