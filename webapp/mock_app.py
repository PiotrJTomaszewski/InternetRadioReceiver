from flask import Flask, render_template, redirect, request
from multiprocessing.managers import SyncManager
from multiprocessing import Queue
from mpd import MPDClient, base

app = Flask(__name__)

shared_song_metadata = {
    'radio': {'name': 'Mock radio test only', 'address': 'https://testonlysite.pl/radio:134'},
    'artist': 'Gloryhammer',
    'track': {
        'name': 'Hail to Crail',
        'tags': [{'url': 'https://tag.com', 'name': 'metal'}, {'url': 'https://tag.com', 'name': 'Hoots'},
                 {'url': 'https://tag.com', 'name': 'Epic'}],
        'wiki': """Gloryhammer released their debut album Tales from the Kingdom of Fife through Napalm Records in March 2013.[4]

On the 25th of September, 2015, Gloryhammer released their second studio album titled Space 1992: Rise of the Chaos Wizards with which the band entered the official album charts in several countries, followed by tours with bands such as Stratovarius, Blind Guardian and Hammerfall.

On the 16th of May, 2017, Gloryhammer was nominated as best band in the category "Up & Coming" of the Metal Hammer Awards 2017 by the German edition of international music magazine Metal Hammer.[5] In 2018, the band was nominated again in the same category.[6]

In January of 2018, the band did a headlining tour across Europe, consisting of 24 shows in a row of which 11 shows were sold out.

In September of 2018, they toured together with Alestorm through North America for the first time, playing 19 shows in the USA and Canada.[7]

On January 30, 2019, the band's official Facebook page announced the album Legends from Beyond the Galactic Terrorvortex, which was released on May 31, 2019. Following the album's release was the band's first North American tour as headliners in June with Æther Realm as support.""",
        'wiki_summary': """Gloryhammer released their debut album Tales from the Kingdom of Fife through Napalm Records in March 2013.[4]

On the 25th of September, 2015, Gloryhammer released their second studio album titled Space 1992: Rise of the Chaos Wizards with which the band entered the official album charts in several countries, followed by tours with bands such as Stratovarius, Blind Guardian and Hammerfall.

On the 16th of May, 2017, Gloryhammer was nominated as best band in the category "Up & Coming" of the Metal Hammer Awards 2017 by the German edition of international music magazine Metal Hammer.[5] In 2018, the band was nominated again in the same category.[6]

In January of 2018, the band did a headlining tour across Europe, consisting of 24 shows in a row of which 11 shows were sold out.

In September of 2018, they toured together with Alestorm through North America for the first time, playing 19 shows in the USA and Canada.[7]

On January 30, 2019, the band's official Facebook page announced the album Legends from Beyond the Galactic Terrorvortex, which was released on May 31, 2019. Following the album's release was the band's first North American tour as headliners in June with Æther Realm as support.""",
    },
    'album': {
        'name': 'Tales from the Kingdom of Fife',

        'wiki': """In a fantasy version of 10th-century Scotland, as previously foretold (“Anstruther’s Dark Prophecy”), the evil wizard Zargothrax invades and conquers Dundee with an army of corrupted undead unicorns (“The Unicorn Invasion of Dundee”), kidnapping the princess Iona McDougall. The prince of the Kingdom of Fife, Angus McFife, swears revenge (“Angus McFife”); in a dream, he has a vision of three artifacts that will allow him to defeat Zargothrax, and sets off on a quest to acquire them.

McFife first battles north to obtain a magical war hammer (“Quest for the Hammer of Glory,”) then travels to Strathclyde to acquire a golden dragon as his steed (“Magic Dragon”). Inspired by memories of McDougall, who is imprisoned by Zargothrax in a prison of ice (“Silent Tears of Frozen Princess,”) McFife rides his dragon to Loch Rannoch and retrieves the Amulet of Justice from its depths (“Amulet of Justice”), completing his quest for the three artifacts.

Allying with the powerful Knights of Crail (“Hail to Crail”), McFife travels through Cowdenbeath (“Beneath Cowdenbeath”) to confront Zargothrax in his stronghold. As the Knights battle the wizard’s forces in the fields of Dunfermline, McFife and the Barbarian Warrior of Unst sneak into the castle through dwarven tunnels, aided by the hermit Ralathor (“The Epic Rage of Furious Thunder”). Meeting Zargothrax in single combat, McFife defeats the wizard and casts him into a frozen pool of “liquid ice.” He then uses the Amulet of Justice to free the princess and the unicorns, restoring balance to the Kingdom of Fife. """,
        'wiki_summary': """Tales from the Kingdom of Fife is the debut album by Anglo-Swiss symphonic power metal band Gloryhammer. It was released on 29 March 2013 in Europe.[1] """,
        'cover_url': 'https://lastfm.freetls.fastly.net/i/u/770x0/4ddbad34b2984b3198b1842a1983c4e0.jpg#4ddbad34b2984b3198b1842a1983c4e0',
        'tags': [{'url': 'https://tag.com', 'name': 'metal'}, {'url': 'https://tag.com', 'name': 'Hoots'},
                 {'url': 'https://tag.com', 'name': 'Epic'}],
        'tracklist': ["Anstruther's Dark Prophecy", "The Unicorn Invasion of Dundee", "Angus McFife",
                      "Quest for the Hammer of Glory", "Magic Dragon", "Silent Tears of Frozen Princess"]
    },
    'release_year': '1992'
}

shared_mpd_status = {
    'state': 'playing',
    'volume': '70'
}

playlist = [{'id': 0, 'title': 'Hard radio', 'name': 'https://www.wp.pl/'},
            {'id': 1, 'title': 'Hardcore radio', 'name': 'https://www.example.com'}]


# global mpd_client, lastfm
# mpd_client = MPDClient()
# mpd_client.connect('localhost', 6600)
# print(mpd_client.mpd_version)


@app.route('/')
def main():
    # mpd_status = mpd_do_action(mpd_client.status)
    # metadata = get_metadata(mpd_client)
    # playlist = mpd_get_playlist()

    #

    return render_template('index.html', metadata=shared_song_metadata, stations=playlist, mpd_status=shared_mpd_status)


@app.route('/pause')
def pause():
    print('Pause')
    # mpd_do_action(mpd_client.pause, 1)
    return redirect('/')


@app.route('/play')
def play():
    print('Play')
    # mpd_do_action(mpd_client.pause, 0)
    return redirect('/')


@app.route('/prev')
def prev_station():
    print('Prev')
    # mpd_do_action(mpd_client.previous)
    return redirect('/')


@app.route('/next')
def next_station():
    print('Next')
    # mpd_do_action(mpd_client.next)
    return redirect('/')


@app.route('/volume_up')
def volume_up():
    print("Vol up")
    return redirect('/')


@app.route('/volume_down')
def volume_down():
    print("Vol down")
    return redirect('/')


@app.route('/switchTo/<station_id>')
def switch_to_station(station_id):
    print('Switch to ', station_id)
    # mpd_do_action(mpd_client.playid, id)
    return redirect('/')


@app.route('/delete/<station_id>')
def delete_station(station_id):
    print('Delete ', station_id)
    # mpd_do_action(mpd_client.deleteid, id)
    return redirect('/')


@app.route('/add_station', methods=['GET'])
def add_station():
    station_address = request.args.get('new_station_address')
    print(station_address)
    return redirect('/')

# TODO: Idle for song change and then force refresh
# TODO: Save playlist
# TODO: Add stations


if __name__ == '__main__':
    app.run()
