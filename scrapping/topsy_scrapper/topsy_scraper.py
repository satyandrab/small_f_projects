#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import with_statement
from __future__ import print_function

import sys
import time
import codecs
import csv
import re
import logging
import logging.handlers
import urllib2
import socket
from StringIO import StringIO
from datetime import datetime
from datetime import timedelta
from random import random

from bs4 import BeautifulSoup


class UnicodeWriter:
    """A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.

    The standard `csv` module isn't able to handle Unicode. We can "cheat" it.
    Firstly, we encode it into plain UTF-8 byte string and write into the
    memory buffer (`StringIO`). Then we convert created CSV data back into
    Unicode and write to the target file.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8"):
        self.buffer = StringIO()
        self.writer = csv.writer(self.buffer, dialect=dialect)
        self.target_stream = f

    def writerow(self, row):
        # Row elements may contain raw Unicode codepoints.
        # We must encode them into UTF-8 (unicode string -> plain byte string).
        encoded_row = [s.encode("utf-8") for s in row]
        # Write encoded row with the standard CSV writer.
        self.writer.writerow(encoded_row)
        # Valid CSV row is now in the memory. Get it ...
        data = self.buffer.getvalue()
        # and convert back into Unicode.
        data = data.decode("utf-8")
        # Now we can easily write valid CSV row in Unicode
        # into the target file.
        self.target_stream.write(data)
        # Empty the buffer.
        self.buffer.truncate(0)


def get_page(url, delay=None):
    """Get page with posible artificial delay.

    The delay is needed to look more like human for the server.

    The delay is determined by `delay` parameter. If `delay` is None (default)
    the delay will be chosen randomly between 0.5 and 2 seconds.
    """

    if not delay:
        delay = 1.5*random()+0.5
    # time.sleep(delay)
    try:
        page = urllib2.urlopen(url, timeout=3).read()
        return page
    except (urllib2.URLError, socket.timeout):
        return None


def get_page_retry(url, n_retries=1):
    """Get page with retries.

    If there is timeout, wait for 5 seconds and retry `n_retries` times.
    """
    for _ in range(n_retries+1):
        page = get_page(url)
        if page:
            return page
        else:
            pass
#        logging.warning('Timeout. Waiting 5 seconds and retry.')
#        time.sleep(5)
#    # If all attempts failed.
#    logging.error('Timeout. Aborted.')
#    return None


def normalize_posting_date(time_text):
    """Parse posting time from string to Python datetime.

    The string can be in two forms:
      - 'month/day/year';
      - 'n (seconds/minutes/hours/days) ago'.
    The second must be considered as relative to the current datetime.

    It's assumed that all dates and times are in UTC time zone.
    """
    m = re.search('^(\d+) (\w+)s', time_text)
    if m:
        n = int(m.group(1))
        units = m.group(2) + 's'  # We always need plural form.
        # Here is some Python magic. For example we have units == 'hours' and
        # n == 3. {units: n} is a dictionary {'hours': 3}. By doing 
        # timedelta(**{units: n}) we do timedelta(**{'hours': 3}) which
        # is equivalent to timedelta(hours=3)
        # (it's how ** operator works here).
        d = timedelta(**{units: n})
        result = datetime.utcnow() - d
    else:
        result = datetime.strptime(time_text, '%m/%d/%Y')
    return result.date()


def parse_tweet(node):
    """Parses tweet node from the page and extracts the following information:
      - user ID (Twitter user handler);
      - user name (human-readable name);
      - tweet text;
      - tweet ID;
      - posting date;
      - retweets count;

    Also hash tags, mentions and links are extracted from tweet text.

    The result is a dictionary representing parsed tweet.
    """
    # Sometimes blocks aren't full, skip it.
    user_id_block = node.find('a', {'class': 'author-link'})
    if not user_id_block:
        return None
    user_id = user_id_block.text
    user_name = node.find('span', {'class': 'author-name'}).text
    tweet_text = node.find('span', {'class': 'twitter-post-text'}).text
    tweet_text = re.sub(r'[\n\r]+', ' ', tweet_text)
    link_to_twitter = node.find('a', {'class': 'date-link'})
    tweet_id = link_to_twitter['href']
    posting_date = normalize_posting_date(link_to_twitter.text)
    retweets_block = node.find('a', {'class': 'trackback-link'})
    # If retweets block exits, extract retweets count. Otherwise, it's 0.
    if retweets_block:
        # Split by spaces to throw away 'more' in the string.
        retweets_count_text = retweets_block.text.split(' ', 1)[0]
        # Remove commas from numbers bigger than 1000.
        retweets_count_text = retweets_count_text.replace(',', '')
        # Replace K with 1000 and M with 1000000 if needed.
        m = re.match('(\d+)(K|M)', retweets_count_text)
        if m:
            retweets_count = int(m.group(1))
            if m.group(2) == 'K':
                retweets_count *= 1000
            elif m.group(2) == 'M':
                retweets_count *= 1000*1000
            else:
                logging.error('Unknown count: {0}', retweets_count_text)
                retweets_count = -1
        else:
            retweets_count = int(retweets_count_text)
    else:
        retweets_count = 0

    # Extract hash tags, mentions and links with regular expressions.
    links_re = re.compile(r'(https?\://[^\s]+)')

    hash_tags = re.findall(r'(?:^|\s)(#\w+)\b', tweet_text, re.U)
    mentions = re.findall(r'(?:^|\s)(@\w+)\b', tweet_text, re.U)
    links = links_re.findall(tweet_text, re.U)

    # Save original tweet text
    original_tweet_text = tweet_text
    # Remove links from tweet text.
    tweet_text = links_re.sub('', tweet_text, re.U)

    result = {
        'user_id': user_id,
        'user_name': user_name,
        'original_tweet_text': original_tweet_text,
        'tweet_text': tweet_text,
        'tweet_id': tweet_id,
        'posting_date': posting_date,
        'retweets_count': retweets_count,
        'hash_tags': hash_tags,
        'mentions': mentions,
        'links': links,
    }
    return result


def parse_page(url):
    """Parse tweets page by the URL.

    The result is a list of tweets of the page.
    """
    page = get_page_retry(url)
    if not page:
        return None

    soup = BeautifulSoup(page, from_encoding='utf-8')
    list_div = soup.find('div', {'class': 'list'})
    if not list_div:
        logging.error("Page {0} doesn't contain list. Skipped.")
        return None

    tweet_boxes_list = list_div.findAll(
        'div', {'class': re.compile('list-(.+?)-v')})

    tweets = []  # List of tweets on the page.
    for node in tweet_boxes_list:
        tweet = parse_tweet(node)
        if tweet:
            tweets.append(tweet)
    return tweets


def get_user_influece(user_id):
    """Get the influence of user with ID `user_id`.

    The result can be "Highly Influential", "Influential" and None.
    """
    logging.info('Finding out influence of "{0}"'.format(user_id))
    url = 'http://topsy.com/twitter/{0}'.format(user_id)
    page = get_page_retry(url)
    if not page:
        return None
    soup = BeautifulSoup(page, from_encoding='utf-8')
    influence_box = soup.find('div', {'class': 'influence-box'})
    if not influence_box:
        return None
    return influence_box.find('span').text


def process_query(url):
    """Process search query determined by `url`.

    Returns a list of tweets and a dictionary of users with theirs influence.
    """
    logging.info('Processing query {0}'.format(url))

    page = get_page_retry(url)
    if not page:
        return None
    soup = BeautifulSoup(page, from_encoding='utf-8')
    # Check if any results.
    no_results_box = soup.find('div', {'class': 'no-results-box'})
    # If no-result-box is detected then there are no results for the query.
    if no_results_box:
        logging.info('No results for query.')
        return None

    # Detect total number of pages.
    pager_box = soup.find('div', {'class': 'pager-box'})
    # If pager-box is detected then there are more than one page
    if pager_box:
        page_n_text = pager_box.find('span', {'class': 'page-number'}).text
        total_pages = int(page_n_text.split(' ')[-1])
    else:
        total_pages = 1

    logging.info('{0} total pages found'.format(total_pages))

    # Collecting tweets from all the pages.
    tweets = []  # List of all found tweets.
    # +1 because `range` doesn't include the last.
    for n in range(1, total_pages+1):
        page_url = '{0}&page={1}'.format(url, n)
        logging.info('Parsing page {0} ({1})'.format(n, page_url))
        page_response = parse_page(page_url)
        if page_response is not None:
            tweets.extend(page_response)
    return tweets


def read_input(input_file_name):
    """Reads the input file and returns a list of URLs.

    Input file can contains both URLs and search queries (one per line). A line
    considered as URL if it starts from 'http://'.

    The function converts queries to URLs.
    """
    logging.info('Reading input file "{0}"'.format(input_file_name))

    URL_TEMPLATE = 'http://topsy.com/s?q={0}'
    
    result = []
    url = ''
    # We use `open` from `codecs` package because it works well with Unicode.
    with codecs.open(input_file_name, mode='r', encoding='utf-8') as f:
        # Read the file by lines.
        for line in f:
            # Remove line breaks and spaces at the beginnig and at the end.
            line = line.strip()
            # Ignore comments.
            if line.startswith('%'):
                continue
            # Ignore empty lines.
            elif len(line) == 0:
                continue
            # If lines starts with 'http://', consider it as URL.
            # Otherwise as query.
            elif line.startswith('http://'):
                url = line
            elif line.startswith(u'@'):
#                logging.info('-'*78)
#                logging.info(line)
#                logging.info('-'*78)
                url = URL_TEMPLATE.format(line)
            else:
                continue
            # Do Percent-encoding to handle Unicode in URL correcty.
            # (https://en.wikipedia.org/wiki/Percent-encoding)

            # We use replacing function in re.sub to replace query substring
            # (which may contain non-ASCII characters) with its percent-encoded
            # equivalent.
            def repl(match):
                query = match.group(1)
                # It's not a universal rule, be here we can consider query
                # already percent-encoded if it contains '%'.
                if '%' in query:
                    # Group 0 - the whole match
                    return match.group(0)
                encoded = urllib2.quote(query.encode('utf-8'))
                return 'q={0}{1}'.format(encoded, match.group(2))

            url = re.sub(r'q=(.+?)($|&)', repl, url, re.U)
            logging.info(url)
            result.append(url)

    logging.info('{0} queries detected.'.format(len(result)))
    return result


def csv_output(tweets, users_influence, f):
    csv_writer = UnicodeWriter(f)

    # Write CSV header.
    csv_writer.writerow([
        'User ID', 'User name', 'User influence', 
        'Tweet text', 'Tweet ID', 'Posting date', 'Retweets',
        'Hash tags', 'Mentions', 'Links'])

    # Write tweets.
    for tw in tweets:
        user_id = tw['user_id']

        # Get user influence from the dictionary and replace it with empty
        # string in case of None.
        user_influence = users_influence[user_id]
        if not user_influence:
            user_influence = ''

        # Create hash tags, mentions ans links strigns combining theirs 
        # lists with commas.
        hash_tags = ','.join(tw['hash_tags'])
        mentions = ','.join(tw['mentions'])
        links = ','.join(tw['links'])

        row = [
            user_id,
            tw['user_name'],
            user_influence,
            tw['tweet_text'],
            tw['tweet_id'],
            str(tw['posting_date']),
            str(tw['retweets_count']),
            hash_tags,
            mentions,
            links]
        csv_writer.writerow(row)


def main(input_file_name, output_file_name):
    # Configure logger which provide a convenient way to output information
    # messages to console and files.
    logging.getLogger().setLevel(logging.INFO)
    # Formatter of log messages.
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    # Log handler for logging to a file.
    file_handler = logging.handlers.RotatingFileHandler(
        'scraper.log', maxBytes=5*(1024**3), backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)

    # Log handler for logging to the console.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

    logging.info('Scraper started.')

    # Will contain all the tweets when the work is finished.
    tweets = []
    # Read queries from the input file and process them.
    urls = read_input(input_file_name)
    
    for url in urls:
        tweets += process_query(url)

    logging.info("Finding out users' influence.")
    # Collecting users set. 
    users = set([t['user_id'] for t in tweets])
    # Finding out each user's influence storing it in a tuple in which
    # the first element is user ID and the second - a string
    # (Highly Influential / Influential) or None.
    users_influence = [(u, get_user_influece(u)) for u in users]
    # Converting the list of tuples into a dictionary. The first element
    # becomes a key, the second - a value.
    users_influence = dict(users_influence)

    logging.info('Writing output CSV.')
    # Write CSV file
    # If file name exists, open file and write into it. Otherwise, use standard
    # output as output file (i.e. write to the console).
    if output_file_name:
        with codecs.open(output_file_name, mode='wb', encoding='utf-8') as f:
            csv_output(tweets, users_influence, f)
    else:
        csv_output(tweets, users_influence, sys.stdout)

    logging.info('Work completed.')


# Standard Python pattern for modules.
if __name__ == '__main__':
    if len(sys.argv) == 2:
        input_file_name = sys.argv[1]
        output_file_name = None
    elif len(sys.argv) == 3:
        input_file_name = sys.argv[1]
        output_file_name = sys.argv[2]
    else:
        print("Usage:")
        # The first element of sys.argv is the script's name.
        print("    {0} input_file [output_file]".format(sys.argv[0]))
        print("If output file isn't specified standard output will be used.")
        exit(1)
    main(input_file_name, output_file_name)
