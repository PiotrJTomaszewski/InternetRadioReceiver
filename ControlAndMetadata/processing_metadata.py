import re


def process_metadata(song):
    return _process_metadata_shoutcast(song)


def _process_metadata_shoutcast(song):
    metadata = {
        'radio_address': song.get('file'),
        'radio_name': song.get('name')}
    title = song.get('title')
    if title is None:
        return {}
    # Check if there is an album release date at the end of the title (Release year is written in parenthesis)
    title = title.rstrip()
    if re.match('\([0-9]{4}\)', title[-6:]):
        metadata['release_year'] = title[-6:]
        # Remove the parenthesis
        metadata['release_year'] = metadata['release_year'][1:-1]
        title = title[:-6].rstrip()
    # Split title and artist (They are usually separated by a '-' signs)
    title_splitted = title.split(' - ')
    if len(title_splitted) == 2:  # If there are both artist and title
        metadata['artist'] = title_splitted[0].rstrip()
        metadata['track'] = title_splitted[1].lstrip()
    elif len(title_splitted) == 1:  # Couldn't split so consider it all a title
        metadata['track'] = title
    else:
        print("Error: The title seems to have more '-' than 2? {}".format(title))
    return metadata


def join_metadata(metadata_from_mpd, track_metadata, album_metadata):
    joined_metadata = {
        'radio': {
            'address': metadata_from_mpd.get('radio_address'),
            'name': metadata_from_mpd.get('radio_name')
        },
        'artist': track_metadata.get('artist') or album_metadata.get('artist') or metadata_from_mpd.get('artist'),
        'track': {
            'name': track_metadata.get('track') or metadata_from_mpd.get('track'),
            'tags': track_metadata.get('tags'),
            'wiki': track_metadata.get('wiki'),
            'wiki_summary': track_metadata.get('wiki_summary')
        },
        'album': {
            'name': album_metadata.get('album') or track_metadata.get('album'),
            'cover_url': album_metadata.get('cover_url'),
            'tags': album_metadata.get('tags'),
            'wiki': album_metadata.get('wiki'),
            'wiki_summary': album_metadata.get('wiki_summary'),
            'tracklist': album_metadata.get('tracklist')
        },
        'release_year': metadata_from_mpd.get('release_year'),
    }
    return joined_metadata


if __name__ == '__main__':
    pass
    # print(process_metadata_shoutcast(
    #     {'file': 'http://144.217.29.205:80/live', 'title': 'Piledriver - Witch Hunt (1234)', 'name': 'HardRadio',
    #      'pos': '0',
    #      'id': '1'}))
