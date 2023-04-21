import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
import itertools

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


def url_generator():
    thread_list = [
        'https://www.mumsnet.com/talk/am_i_being_unreasonable/4676538-if-you-like-wordle-plusword-is-even-better-thread-4?page=',
        # 'https://www.mumsnet.com/talk/_chat/4714295-plusword-new-thread-1?page=',
        # 'https://www.mumsnet.com/talk/_chat/4765702-plusword-new-thread-2?page='
    ]

    url_list = []

    for thread in thread_list:
        for page_number in range(1, 41):
            url = thread + str(page_number)
            url_list.append(url)

    return url_list


def multithread_scraper(url):
    # gets web pages
    with requests.get(url, allow_redirects=False) as r:

        # returns None if url redirects you to main page
        # happens if page number is higher than current page count
        if r.status_code != 302:

            soup = BeautifulSoup(r.content, features="html5lib")

            post_list = []

            # selects first page as we need original post
            if url[-2:] == '=1':

                original_post_list = []

                # selects post info and body and drops title and other stuff we dont need
                original_post = soup.find('div', class_=original_post_class)
                original_post = original_post.find_all('div', class_='')[2].find_all('p')

                paragraph_list = []
                for paragraph in original_post:
                    post_text = paragraph.getText().split()
                    post_text = ' '.join(post_text)
                    paragraph_list.append(post_text)

                meta_data = paragraph_list[0].split()
                del meta_data[1]
                meta_data.append(paragraph_list[1])
                original_post = meta_data
                original_post_list.append(original_post)

                # flattens list
                original_post = [val for sublist in original_post_list for val in sublist]

                return (original_post)

            else:

                posts = soup.find_all('div', class_=[normal_post_class, original_poster_reply_class])

                # deletes body of op which is scraped again
                del posts[0]

                for post in posts:
                    post_text = post.getText().split()

                    # separates out meta data and post body
                    meta_data = post_text[:4]
                    post_body = post_text[4:]

                    # removes fullstop from meta data
                    meta_data.pop(1)

                    # converts whole of post body to one string
                    post_body = ' '.join(post_body)
                    meta_data.append(post_body)
                    whole_post = meta_data

                return (whole_post)

        return


modified_start = time.time()
result_list = []
url_list = url_generator()

# Runs scraper
with ThreadPoolExecutor() as executor:
    results = executor.map(multithread_scraper, url_list)
    for result in results:
        if result != None:
            result_list.append(result)

df = pd.DataFrame(result_list, columns=['user', 'date', 'time', 'text'])

modified_end = time.time()
modified_time = modified_end - modified_start

