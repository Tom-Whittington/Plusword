import pandas as pd
from bs4 import BeautifulSoup
import requests
import datetime as dt
from plotting_streamlit import data_import, get_db


def get_urls():
    """ Historic list of urls we're scraping from as well as the current one. Needs to be changed when a new thread
    is made"""

    url_list = [
        # 'https://www.mumsnet.com/talk/am_i_being_unreasonable/4676538-if-you-like-wordle-plusword-is-even-better-thread-4?page=',
        # 'https://www.mumsnet.com/talk/_chat/4714295-plusword-new-thread-1?page=',
        'https://www.mumsnet.com/talk/_chat/4765702-plusword-new-thread-2?page=']

    return url_list


def scraper(url_list):
    """ Loops over all the different types of posts on the mumsnet website, accessing the text values. Then appends
    them to a list which is finally converted to a dataframe and returned"""

    whole_post_list = []

    # maximum number of pages in thread
    max_pages = 41

    # html class of original post from the thread
    first_post_class = 'p-4 pb-1 pt-2.5 lg:py-2.5 mt-2.5 lg:mt-1.5 border-t border-b sm:border sm:rounded ' \
                       'border-mumsnet-forest-border bg-mumsnet-forest dark:bg-mumsnet-forest-dark'

    # html class of a normal post from the thread
    normal_reply_class = 'lg:py-2.5 pt-2.5 pb-1 p-4 border-t border-b sm:border sm:rounded mt-1.5 overflow-x-hidden ' \
                         'bg-white dark:bg-gray-800 border-gray-200'

    # html class of a post from the thread creator
    original_poster_reply_class = 'lg:py-2.5 pt-2.5 pb-1 p-4 border-t border-b sm:border sm:rounded mt-1.5 ' \
                                  'overflow-x-hidden bg-mumsnet-forest dark:bg-mumsnet-forest-dark ' \
                                  'border-mumsnet-forest-border'

    for url in url_list:

        # Increments through every page on website until it runs out for hits max_pages
        for page_number in range(max_pages):

            try:

                # gets request via bs4
                r = requests.get(url + str(page_number))
                soup = BeautifulSoup(r.content, features="html5lib")

                # Finds original post on each page and splits it into metadata and post text
                original_post = soup.find_all('div', class_=first_post_class)
                original_post_paragraphs = original_post[0].find_all('p')

                # converts to list
                meta_data = original_post_paragraphs[0].getText().split()

                # removes fullstops in position 1
                meta_data.pop(1)

                # converts text to list and then joins items together
                post_text = original_post_paragraphs[1].getText().split()
                post_text = ' '.join(post_text)

                # Adds OP metadata and text together and adds together for OP on every page
                meta_data.append(post_text)
                whole_post = meta_data
                whole_post_list.append(whole_post)

                # finds all non-OP post on page and gets data
                posts = soup.find_all('div', class_=[normal_reply_class, original_poster_reply_class])

                for post in posts:
                    post_info = post.getText().split()

                    # first 4 items are meta data
                    meta_data = post_info[:4]

                    # removes unneeded full stop
                    meta_data.pop(1)

                    # joins post text together
                    post_text = post_info[4:]
                    post_text = ' '.join(post_text)

                    # appends metadata and text together and adds to list
                    meta_data.append(post_text)
                    whole_post = meta_data
                    whole_post_list.append(whole_post)

            except Exception as e:
                print(e)
            pass

    df = pd.DataFrame(whole_post_list, columns=['user', 'date', 'time', 'text'])

    return df


def data_cleaning(df):
    """ Cleans up data ready for adding to db"""

    # Converts 'Today' and 'Yesterday' into datetime values
    df['date'] = df['date'].str.replace('Yesterday',
                                        dt.datetime.strftime((dt.datetime.today() - dt.timedelta(days=1)), '%d/%m/%Y'))
    df['date'] = df['date'].str.replace('Today', dt.datetime.strftime(dt.datetime.today(), '%d/%m/%Y'))

    # Creates timestamp column from date and time, adds some milliseconds to the string before converting to datetime
    # and sorting
    df['load_ts'] = df['date'] + ' ' + (df['time'] + ':00')
    df['load_ts'] = df['load_ts'] + '.000'
    df['load_ts'] = pd.to_datetime(df['load_ts'], format='%d/%m/%Y %H:%M:%S.%f')
    df = df.sort_values(by=['load_ts'])

    # Extracts times from scraped post text
    df['text'] = df['text'].str.extract(r'(\d*\d:\d\d)')

    # drops any rows with no recognised times in, adds a zero to any minutes represented by a single 0 and adds 00:
    # to deal with hours
    df = df.dropna(subset='text')
    df = df.copy()
    df['text'] = df['text'].str.replace(r'(^\d:\d\d)', r'0\1', regex=True)
    df['text'] = '00:' + df['text']

    # drops duplicate posts from same user on same day and formats columns
    df = df.copy()
    df = df.drop_duplicates(subset=['user', 'date'])
    df = df.drop(columns=['date', 'time'])
    df = df.rename(columns={'text': 'time'})
    df = df[['load_ts', 'time', 'user']]

    return df


def filter_out_old_rows(df):
    """ Gets data from database and filters out rows that are already in the database"""

    df_mums = data_import('Mumsnet_Times')
    df = df.set_index(['load_ts', 'user'])
    df_mums = df_mums.set_index(['load_ts', 'user'])
    df = df[~df.index.isin(df_mums.index)].reset_index()

    return df


def data_export(df):
    """ If dataframe isn't empty then rows are written to the database"""
    if not df.empty:
        try:
            db = get_db(write=True)
            collection = db['Mumsnet_Times']
            collection.insert_many(df.to_dict('records'))
        except Exception as e:
            print(e)


def main():
    url_list = get_urls()
    df = scraper(url_list)
    df = data_cleaning(df)
    df = filter_out_old_rows(df)
    data_export(df)


if __name__ == "__main__":
    main()
