import pandas as pd
from bs4 import BeautifulSoup
import requests
import datetime as dt


def urls():
    url_list = [
        #'https://www.mumsnet.com/talk/am_i_being_unreasonable/4676538-if-you-like-wordle-plusword-is-even-better'
        #'-thread-4?page=',
        #'https://www.mumsnet.com/talk/_chat/4714295-plusword-new-thread-1?page=',
        'https://www.mumsnet.com/talk/_chat/4765702-plusword-new-thread-2?page=']
    return (url_list)


def scraper(url_list):

    whole_post_list = []

    # maxiumum number of pages in thread
    max_pages = 41

    for url in url_list:

        # Increments through every page on website until it runs out for hits max_pages
        for page_number in range(max_pages):

            try:

                # gets request via bs4
                r = requests.get(url + str(page_number))
                soup = BeautifulSoup(r.content, features="html5lib")

                # Finds original post on each page and splits it into metadata and post text
                original_post = soup.find_all('div',
                                              class_='p-4 pb-1 pt-2.5 lg:py-2.5 mt-2.5 lg:mt-1.5 border-t border-b '
                                                     'sm:border sm:rounded border-mumsnet-forest-border bg-mumsnet-forest '
                                                     'dark:bg-mumsnet-forest-dark')
                original_post_paragraphs = original_post[0].find_all('p')

                # converts to list
                meta_data = original_post_paragraphs[0].getText().split()

                # removes fullstop in position 1
                meta_data.pop(1)

                # converts text to list and then joins items together
                post_text = original_post_paragraphs[1].getText().split()
                post_text = ' '.join(post_text)

                # Adds OP metadata and text together and adds together for OP on every page
                meta_data.append(post_text)
                whole_post = meta_data
                whole_post_list.append(whole_post)

                # finds all non-OP post on page and gets data
                posts = soup.find_all('div',
                                      class_='lg:py-2.5 pt-2.5 pb-1 p-4 border-t border-b sm:border sm:rounded mt-1.5 '
                                             'overflow-x-hidden bg-white dark:bg-gray-800 border-gray-200')
                for post in posts:
                    post_info = post.getText().split()

                    # first 4 items are meta data
                    meta_data = post_info[:4]

                    # removes uneeded full stop
                    meta_data.pop(1)

                    # joins post text together
                    post_text = post_info[4:]
                    post_text = ' '.join(post_text)

                    # appends metadata and text together and adds to list
                    meta_data.append(post_text)
                    whole_post = meta_data
                    whole_post_list.append(whole_post)
            except:
                pass

    df = pd.DataFrame(whole_post_list, columns=['user', 'date', 'time', 'text'])

    return df



def data_cleaning(df):

    df['date'] = df['date'].str.replace('Yesterday',
                                        dt.datetime.strftime((dt.datetime.today() - dt.timedelta(days=1)),'%d/%m/%Y'))

    df['date'] = df['date'].str.replace('Today', dt.datetime.strftime(dt.datetime.today(), '%d/%m/%Y'))
    df['load_ts'] = pd.to_datetime(df['date'] + ' ' + (df['time'] + ':00'), format='%d/%m/%Y %H:%M:%S')
    df = df.sort_values(by=['load_ts'])

    # Extracts times from text
    df['text'] = df['text'].str.extract(r'(\d*\d:\d\d)')

    # Drops rows with no times in
    df = df.dropna(subset='text')
    df = df.copy()

    # adds a 0 to the value if minutes expressed as single digit
    df['text'] = df['text'].str.replace(r'(^\d:\d\d)', r'0\1', regex=True)

    # adds hours
    df['text'] = '00:' + df['text']

    # Drops duplicate entries for users on same date, drops columns and renames
    df = df.copy()
    df = df.drop_duplicates(subset=['user', 'date'])
    df = df.drop(columns=['date', 'time'])
    df = df.rename(columns={'text': 'time'})
    df = df[['load_ts', 'user', 'time']]

    # Prints csv
    df.to_csv('data/mumsnet_data.csv', index=False)


def main():
    url_list = urls()
    df = scraper(url_list)
    data_cleaning(df)


if __name__ == "__main__":
    main()
