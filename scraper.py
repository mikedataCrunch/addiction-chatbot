import logging
import argparse
import requests
import json
import time
import random
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import unicodedata
import os
import re


proxies = {
    'http': 'http://206.189.157.23',
    'http': 'http://206.189.157.23'
}

def init_logger():
    logging.basicConfig(
        filename=f'{args.save_dir}-scrape.log',
        # filemode='w', # overwrite
        level=logging.INFO,
        format="%(asctime)-15s %(message)s"
    )
    return logging.getLogger()


def clean_text(text):
     # fix formatting, decode without the BOM (byte order mark)
    text = text.encode('iso-8859-1').decode('utf-8-sig')
    text = unicodedata.normalize('NFKD', text)
    return text

def load_urls():
    # read the file
    filename = args.source_file
    with open(filename) as f:
        urls_list = [tuple(x) for x in json.load(f)]
    return urls_list
    
def get_data(url):    
    try:
        response = requests.get(url, proxies=proxies)
        logger.info(
            f"""\nSuccess in getting data!\nResponse code: {response.status_code}\nEncoding: {response.encoding}\n"""
            )
        return response.text
    
    except BaseException as e:
        logger.error(f'Failed to get page {page}: {str(e)}')
        pass

def get_title(soup):
    try:
        title = clean_text(soup.head.title.text)
        logger.info("get_title success!")
        return title
    except BaseException as e:
        logger.error(f'get_title failed: {str(e)}')
        pass

def get_kicker(soup):    
    try:    
        kicker = clean_text(soup.select_one('p#kicker1.kicker').text)
        logger.info("get_kicker success!")
        return kicker

    except BaseException as e:
        logger.error(f'get_kicker failed: {str(e)}')
        pass
    
def get_body(soup):
    try:
        body_element = soup.find('div', {"class":'body-block'})
        body_text = []
        for p in body_element.find_all('p'):
            # fix formatting, decode withou the BOM (byte order mark)
            paragraph = clean_text(p.text)
            body_text.append(paragraph)
        body = "\n".join(body_text)
        logger.info("get_body success!")
        return body

    except BaseException as e:
        logger.error(f'get_body failed: {str(e)}')
        pass

def get_author(soup):
    try:
        bylines = soup.find_all('div', {'class' : 'byline'})
        author = clean_text(bylines[0].find(id='p1').text)
        author = re.sub('By ', '', author)
        logger.info("get_author success!")
        return author
    
    except BaseException as e:
        logger.error(f'get_author failed: {str(e)}')
        pass

def get_calling(soup):
    try:
        bylines = soup.find_all('div', {'class' : 'byline'})
        calling = clean_text(bylines[0].find(id='p2').text)
        logger.info("get_calling success!\n")
        return calling
    
    except BaseException as e:
        logger.error(f'get_calling failed: {str(e)}\n\n')
        pass

def scrape():
    urls_list = load_urls()
    if args.select_index:
        indexes = [int(i) for i in arg.select_index.split(',')]
        urls_list = [i for i in urls_list if i in indexes]
        logger.info(f"Scraping on select urls: {args.select_index}\n")
    elif args.start_index:
        if args.end_index:
            urls_list = urls_list[args.start_index: args.end_index]
            logger.info(f"Scraping on range {args.start_index} to {args.end_index}\n")
    else:
        logger.info("Scraping all urls!\n")
        pass
    missing_report = {
        'title': [],
        'kicker': [],
        'body': [],
        'author': [],
        'calling': []
    }
    for page, index, url in tqdm(urls_list):
        # get data from page
        logger.info(f"Scraping index {index} from page {page}!\n")
        page_data = get_data(url)
        soup = bs(page_data, 'html.parser')
        
        title = get_title(soup)
        if not title:
            missing_report['title'].append(index)
            
        kicker = get_kicker(soup)
        if not kicker:
            missing_report['kicker'].append(index)
            
        body = get_body(soup)
        if not body:
            missing_report['body'].append(index)
            
        author = get_author(soup)
        if not author:
            missing_report['author'].append(index)
            
        calling = get_calling(soup)
        if not calling:
            missing_report['calling'].append(index)
        
        # parse and scrape
        data = {
            'page': page,
            'index': index,
            'title' : title,
            'kicker' : kicker,
            'body' : body,
            'author' : author,
            'calling' : calling,
            'url': url
        }
        # save
        if not os.path.exists(args.save_dir):
            os.makedirs(args.save_dir)
        filename = os.path.join(
            args.save_dir, 
            f"{args.save_dir}-{page}-{index}.json"
        )
        # write data in new file each time
        with open(filename, 'w') as f:
            json.dump(data, f)
        time.sleep(random.randrange(3, 8))
 
        # save missing report : overwrite at every loop
        with open(f'{args.save_dir}-missing-report.json', 'w') as f:
            json.dump(missing_report, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Extract page urls returned by searching the base url."
    )
    parser.add_argument(
        "--source_file", type=str, help="Source file for urls to scrape.",
        required=True
    )
    parser.add_argument(
        "--save_dir", type=str, help="Select facet dir from [data/general-conference, data/magazines]",
        required=True
    )
    parser.add_argument(
        "--select_index", type=str, help="Select index for non-range scraping.",
        default=None
    )
    parser.add_argument(
        "--start_index", type=int, help="Starting index for selective scraping",
        default=None
    )
    parser.add_argument(
        "--end_index", type=int, help="End index for selective scraping",
        default=None
    )

    args = parser.parse_args()
    logger = init_logger()
    print(f"Scraping {args.save_dir} pages...")
    scrape()
    print("Done.")