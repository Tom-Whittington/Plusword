import datetime as dt
import re
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from plotting_streamlit import get_db, data_import


# TODO: Add dynamic max page finder based on incrementing through pages until direct is triggered


def mumsnet_url_generator():
    """ Generates list of urls to scrape from """

    # Append new threads here

    thread_list = [
        # 'https://www.mumsnet.com/talk/am_i_being_unreasonable/4676538-if-you-like-wordle-plusword-is-even-better-thread-4?page=',
        # 'https://www.mumsnet.com/talk/_chat/4714295-plusword-new-thread-1?page=',
        'https://www.mumsnet.com/talk/_chat/4765702-plusword-new-thread-2?page='
    ]

    url_list = []

    for thread in thread_list:
        for page_number in range(1, 41):
            url = thread + str(page_number)
            url_list.append(url)

    return url_list


def mumsnet_post_to_text_converter(post):
    """ Converts each post from html to text, then formats and appends metadata to the post body"""

    # converts to list and removes whitespace
    post_text = post.getText().split()

    # separates out meta data and post body
    meta_data = post_text[:4]
    post_body = post_text[4:]

    # removes fullstop from meta data
    meta_data.pop(1)

    # converts whole of post to list
    post_body = ' '.join(post_body)
    meta_data.append(post_body)
    whole_post = meta_data

    return whole_post


def mumsnet_scraper(url):
    # html class of original post from the thread
    original_post_class = 'p-4 pb-1 pt-2.5 lg:py-2.5 mt-2.5 lg:mt-1.5 border-t border-b sm:border sm:rounded ' \
                          'border-mumsnet-forest-border bg-mumsnet-forest dark:bg-mumsnet-forest-dark'

    # html class of a normal post from the thread
    normal_post_class = 'lg:py-2.5 pt-2.5 pb-1 p-4 border-t border-b sm:border sm:rounded mt-1.5 overflow-x-hidden ' \
                        'bg-white dark:bg-gray-800 border-gray-200'

    # html class of a post from the thread creator
    original_poster_reply_class = 'lg:py-2.5 pt-2.5 pb-1 p-4 border-t border-b sm:border sm:rounded mt-1.5 ' \
                                  'overflow-x-hidden bg-mumsnet-forest dark:bg-mumsnet-forest-dark ' \
                                  'border-mumsnet-forest-border'

    # gets web pages
    with requests.get(url, allow_redirects=False) as r:

        # returns None if url redirects you to main page
        # happens if page number is higher than current page count
        if r.status_code != 302:

            soup = BeautifulSoup(r.content, features="html5lib")

            all_posts_in_url = []

            # selects first page as we need original post
            if url[-2:] == '=1':
                # Finds original post on first page and splits it into metadata and post text
                original_post = soup.find_all('div', class_=original_post_class)
                original_post = original_post[0].find_all('div', class_='')
                original_post = mumsnet_post_to_text_converter(original_post[2])
                all_posts_in_url.append(original_post)

            # selects post info and body and drops title and other stuff we don't need
            posts = soup.find_all('div', class_=[normal_post_class, original_poster_reply_class])
            for post in posts:
                whole_post = mumsnet_post_to_text_converter(post)
                all_posts_in_url.append(whole_post)

        # returns None if redirected
        else:
            return

    return all_posts_in_url


def mumsnet_multithread_wrapper(url_list):
    """ Scrapes each page in url list for data and appends results together and creates df from data"""

    all_posts = []

    # Runs scraping script over each item in url list with multithreading
    # Then appends
    with ThreadPoolExecutor() as executor:
        all_posts_in_url = executor.map(mumsnet_scraper, url_list)
        for page in all_posts_in_url:
            all_posts.append(page)

    # Removes any None values from exiting function early
    all_posts = [x for x in all_posts if x is not None]

    # Drops list level
    all_posts = [val for sublist in all_posts for val in sublist]

    df = pd.DataFrame(all_posts, columns=['user', 'date', 'time', 'text'])

    return df


def mumsnet_cleaning(df):
    """ Cleans up data ready for adding to db"""

    # replace 'Today' and 'Yesterday with datetime values'
    df['date'] = df['date'].str.replace('Yesterday',
                                        dt.datetime.strftime((dt.datetime.today() - dt.timedelta(days=1)), '%d/%m/%Y'))
    df['date'] = df['date'].str.replace('Today', dt.datetime.strftime(dt.datetime.today(), '%d/%m/%Y'))

    # creates timestamp column with seconds and milliseconds, converts to datetime and sorts by timestamp
    df['load_ts'] = df['date'] + ' ' + (df['time'] + ':00.000')
    df['load_ts'] = pd.to_datetime(df['load_ts'], format='%d/%m/%Y %H:%M:%S.%f')
    df = df.sort_values(by=['load_ts'])

    # extracts time from text and drops any rows without a valid time
    df['text'] = df['text'].str.extract(r'(\d*\d:\d\d)')
    df = df.dropna(subset='text')
    df = df.copy()

    # adds a padding 0 to adding times with minutes represented by single digits, and adds hour values
    df['text'] = df['text'].str.replace(r'(^\d:\d\d)', r'0\1', regex=True)
    df['text'] = '00:' + df['text']

    # drops columns and renames
    df = df.copy()
    df = df.drop_duplicates(subset=['user', 'date'])
    df = df.drop(columns=['date', 'time'])
    df = df.rename(columns={'text': 'time'})
    df = df[['load_ts', 'time', 'user']]

    return df


def filter_out_old_rows(df, collection_name, index_columns):
    """ Gets data from database and filters out rows that are already in the database"""

    df_db = data_import(collection_name)
    df = df.set_index(index_columns)
    df_db = df_db.set_index(index_columns)
    df = df[~df.index.isin(df_db.index)].reset_index()

    return df


def data_export(df, collection_name):
    """ If dataframe isn't empty then rows are written to the database"""
    if not df.empty:
        print('something in df')
        try:
            db = get_db(write=True)
            collection = db[collection_name]
            collection.insert_many(df.to_dict('records'))
        except Exception as e:
            print(e)
    print('empty_df')


def get_plus_word():
    url = 'https://puzzles-prod.telegraph.co.uk/plusword/data.json'
    r_json = requests.get(url).json()

    row = {'date': r_json['copy']['date-publish-analytics'][:10],
           'puzzle_number': r_json['meta']['number'],
           'plusword_solution': r_json['settings']['solution']}

    for direction in ['across', 'down']:
        clue_num = 0
        for clue in r_json['cluedata'][direction]:
            clue_num += 1
            row.update({'clue_' + direction + '_' + str(clue_num): clue})

    for answer_num in range(1, 6):
        row.update({'answer_' + str(answer_num): r_json['celldata'][5 * (answer_num - 1):(5 * answer_num)]})

    url = 'https://puzzles-prod.telegraph.co.uk/plusword/index.html'
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    driver.find_element(By.XPATH, '/html/body/div[2]/div[5]/header/button').click()

    yellow = []
    green = []
    match = 'C\d*'
    for table_row in driver.find_elements(By.CLASS_NAME, "row"):
        for cell in table_row.find_elements(By.TAG_NAME, 'td'):
            cell_class = cell.get_attribute("class")

            if 'right-letter-wrong-column' in cell_class:
                yellow.append(int(re.search(match, cell_class).group(0).strip('C')) + 1)

            if 'right-letter-right-column' in cell_class:
                green.append(int(re.search(match, cell_class).group(0).strip('C')) + 1)

    row.update({'yellow': yellow,
                'green': green})

    df = pd.DataFrame.from_dict([row])
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df = df.replace('"', '', regex=True)
    df = df.replace("&#039", '', regex=True)
    df = df.replace(';', '', regex=True)

    return df


def puzzle_export():
    df = get_plus_word()
    df = filter_out_old_rows(df, 'Puzzle_Data', 'date')
    data_export(df, 'Puzzle_Data')


def mumsnet_export():
    url_list = mumsnet_url_generator()
    df_raw = mumsnet_multithread_wrapper(url_list)
    df_clean = mumsnet_cleaning(df_raw)
    df = filter_out_old_rows(df_clean, 'Mumsnet_Times', ['load_ts', 'user'])
    data_export(df, 'Mumsnet_Times')


def main():
    puzzle_export()
    mumsnet_export()


if __name__ == "__main__":
    main()
