from lyrics import *
from operator import itemgetter

import os
import re
import argparse
import logging

"""
Begin constants ================================================================
"""
# Matches a line from a by_year CSV.
# Example: myword, 3 -> group(1) = myword, group(2) = 3
LINE_REGEX = re.compile('(\S+),\s*(\d+)')

# Matches a by_year filename.
# Example: 1983.csv -> group(1) = 1983
FILENAME_REGEX = re.compile('(\w+).csv')
"""
End constants ==================================================================
"""


def parse_year_from_string(date_string):
    """
    Given date_string where numbers are separated by -, return largest
    number in the string.
    """

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


def clean_lyrics(lyrics, to_ignore=[]):
    """
    Removes specified words from a string (lyrics) by replacing them with
    empty strings. Returns modified string.
    """
    ignored_phrases = [
        "******* This Lyrics is NOT for Commercial use *******"
    ]

    ignored_phrases.extend(to_ignore)

    for item in ignored_phrases:
        lyrics = lyrics.replace(item, "")

    return lyrics


def clean_filename(filename):
    """
    Remove non-word characters from filename.
    """
    return re.sub("[^\'\w]|[\.]+", "", filename)


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


def word_count_by_word(artist_name, words=[]):
    """
    Given a word and an artist, process the artist's by_year CSV files
    and get the number of occurrences of word for each year. Writes results
    to output/by_word/<word>.csv
    """
    if not artist_name and word:
        logging.error("Artist name and word to count are required.")
        return

    by_year_path = "output/{}/by_year".format(artist_name)
    by_word_path = "output/{}/by_word".format(artist_name)

    # create by_word directory if it DNE already
    if not os.path.exists(by_word_path):
        os.makedirs(by_word_path)

    for word in words:
        listing = os.listdir(by_year_path)
        f = open("{}/{}.csv".format(by_word_path, clean_filename(word)), 'w')

        for infile in listing:
            try:
                file = open("{}/{}".format(by_year_path, infile), 'r')

                for line in file:
                    line_match = LINE_REGEX.match(line)

                    if line_match and line_match.group(1) == word:
                        filename_match = FILENAME_REGEX.match(infile)
                        year = filename_match.group(1)
                        word_count = line_match.group(2)

                        # write line to by_word file
                        word = word.replace(',', '')
                        word_line = "{}, {}\n".format(year, word_count)
                        f.write(word_line)
            except Exception as e:
                pass

        f.close()


def list_words_from_all_years(artist_name):
    """
    Returns a list of all words used at least once throughout the artist's
    entire collection of by_year files.
    """
    if not artist_name and word:
        logging.error("Artist name is required.")
        return

    by_year_path = "output/{}/by_year".format(artist_name)
    listing = os.listdir(by_year_path)
    word_set = set()

    for infile in listing:
        file = open("{}/{}".format(by_year_path, infile), 'r')

        for line in file:
            match = LINE_REGEX.match(line)

            if match:
                word = match.group(1)
                word_set.add(word)

        file.close()

    return word_set


def write_count_to_file(count_dict, artist_name=None):
    """
    Given a dict containing years and dicts of word counts,
    create a file for each year. Then, for each word/count in that year,
    write a comma-separated line to that year's file.
    """
    directory = "output"

    if artist_name:
        directory += "/{}".format(artist_name)

    directory += "/by_year"

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
    parser = argparse.ArgumentParser(description='Count frequency of words in lyrics')
    parser.add_argument(
        '--fetch-lyrics',
        action='store_true',
        help='Download and process lyrics by year from MusixMatch'
    )
    parser.add_argument(
        '-a', '--artist-name',
        help='Name of artist to process'
    )
    parser.add_argument(
        '-w', '--word',
        help='Word to create by_word file for'
    )
    parser.add_argument(
        '--count-all-words',
        action='store_true',
        help='Create by_word file for all words used by artist'
    )

    args = vars(parser.parse_args())
    artist_name = args['artist_name']
    word = args['word']
    count_all_words = args['count_all_words']
    fetch_lyrics = args['fetch_lyrics']

    if fetch_lyrics:
        count = word_count_by_year(artist_name)
        write_count_to_file(count, artist_name)

    if word or count_all_words:
        words = list_words_from_all_years(artist_name) if count_all_words else [word]
        word_count_by_word(artist_name, words)
