import logging
import argparse
import requests
import json
import time
import random
from tqdm import tqdm
from bs4 import BeautifulSoup as bs

proxies = {
    'http': 'http://206.189.157.23',
    'http': 'http://206.189.157.23'
}

def init_logger():
    logging.basicConfig(
        filename=f'logs/{args.facet}-crawl.log',
        # filemode='w', # overwrite
        level=logging.INFO,
        format="%(asctime)-15s %(message)s"
    )
    return logging.getLogger()

    
def get_page(base_url, page, facet):
    get_payload = {
        'highlight':'true',
        'page': page,
        'facet': facet
    }
    response = requests.get(
        base_url, 
        params=get_payload,              
        proxies=proxies)
    return response

def get_urls(page, response, index):
    soup = bs(response.text,  'html.parser')
    a_tags = soup.find_all('a', {'class' : 'sc-fodVek kfdvrS'})
    url_list = []
    for a_tag in a_tags:
        url = a_tag.get('href')
        url_list.append((page, index, url))
        index += 1
    return index, url_list

def main():
    logger.info(f"\n{'-'*80}\nGetting urls for addiction recovery from {args.facet}\nPages {args.start_page}-{args.end_page}\n{'-'*80}")
    
    main_url_list = []
    index = args.last_index
    for page in tqdm(range(args.start_page, args.end_page + 1)):
        try:
            response = get_page(args.base_url, page, args.facet)
            index, page_url_list = get_urls(page, response, index)
            main_url_list.extend(page_url_list)
            logger.info(
                f"""\nSuccess in getting page: {page}\nResponse code: {response.status_code}\nEncoding: {response.encoding}\n"""
            )
        except BaseException as e:
            logger.error(f'Failed to get page {page}: {str(e)}')
            pass
        
    # save as json
    with open(args.save_file, 'w') as f:
        json.dump(main_url_list, f)
        
    time.sleep(random.randrange(5, 12))

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Extract page urls returned by searching the base url."
    )
    parser.add_argument(
        "--base_url", type=str, help="Base url to crawl.",
        required=True
    )
    parser.add_argument(
        "--facet", type=str, help="Select facet from [general-conference, magazines]", 
        required=True
    )
    parser.add_argument(
        "--start_page", type=int, help="Starting page to parse.", 
        required=True
    )
    parser.add_argument(
        "--end_page", type=int, help="Ending page to parse.", 
        required=True
    )
    parser.add_argument(
        "--last_index", type=int, help="Last index in logs.", 
        required=True
    )
    parser.add_argument(
        "--save_file", type=str, help="Json file to save page urls to.",
        required=True
    )
    args = parser.parse_args()
    logger = init_logger()
    print(f"Crawling {args.facet} pages {args.start_page} to {args.end_page}...")
    main()
    print("Done.")