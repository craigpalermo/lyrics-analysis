from lyrics import *
from operator import itemgetter

import os


def parse_year_from_string(date_string):
    '''
    Given date_string where numbers are separated by -, return largest
    number in the string.
    '''

    split = date_string.split('-')

    if len(split) > 1:
        sorted_arr = sorted(list(map(lambda x: int(x), split)), reverse=True) 
        return str(sorted_arr[0])

    return split[0]


def get_top_words(year_dict):
    word_tuples = []

    # convert dict to list of tuples
    for word, count in year_dict.items():
        word_tuples.append((word, count))

    # sort list by count descending
    return sorted(word_tuples, key=itemgetter(1), reverse=True)


def clean_lyrics(lyrics):
    ignored_phrases = ["******* This Lyrics is NOT for Commercial use *******"]
    
    for item in ignored_phrases:
        lyrics = lyrics.replace(item, "")

    return lyrics


def word_count_by_year(artist_name):
    artist_id = get_artist_id(artist_name)
    albums = get_albums(artist_id)
    results = {}
    seen_albums = set()

    # iterate list of albums and count words for each album's tracks
    for album in albums:
        album_id = album['album']['album_id']
        release_date = parse_year_from_string(album['album']['album_release_date'])
        album_name = album['album']['album_name']
        tracks = get_tracks(album_id)
        
        # process unseen albums
        if not album_name in seen_albums:
            print(u"Processing: {} ({})".format(album['album']['album_name'], release_date))
            seen_albums.add(album_name)

            if not results.get(release_date):
                results[release_date] = {}

            cur_year = results[release_date]

            for track in tracks:
                track_id = track['track']['track_id']
                lyrics = get_lyrics(track_id)
                lyrics = clean_lyrics(lyrics)
                lyrics_array = lyrics.split()

                for word in lyrics_array:
                    word = word.lower()

                    if not cur_year.get(word):
                        cur_year[word] = 0

                    cur_year[word] += 1

    return results


def write_count_to_file(count_dict):
    '''
    Given a dict containing years and dicts of word counts,
    create a file for each year. Then, for each word/count in that year,
    write a comma-separated line to that year's file.
    '''
    directory = "output"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for year, words in count_dict.items():
        f = open("{}/{}.csv".format(directory, year), 'w')

        for word, count in words.items():
            # remove commas from word
            word = word.replace(',', '')

            word_line = "{}, {}\n".format(word, count)
            f.write(word_line)

        f.close()


if __name__ == "__main__":
    count = word_count_by_year('metallica')
    write_count_to_file(count)
