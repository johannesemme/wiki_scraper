import json
from tqdm import tqdm
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import argparse

def get_title_and_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.findAll('h1',attrs={'id':"firstHeading"})[0].text
    text = soup.findAll('div',attrs={'id':"mw-content-text"})[0]
    for tbody in text.findAll('tbody'): # remove all tables
        tbody.decompose()
    for div in text.findAll('div',attrs={'class':"thumbcaption"}): # remove all captions for images
        div.decompose()    
    text = text.prettify()
    return title.strip(), text.strip()

def get_raw_data(url):
    """ Get plain text from a wikipedia page"""
    title, text = None, None
    try:
        title, text = get_title_and_text(url)
    except:
        print(f"Failed for url: {url}. We try to obtain the wikitext again in 5 seconds...")
        try:
            time.sleep(5)
            title, text = get_title_and_text(url)
        except:
            print("Failed again - no text is collected.")
    return title, text


def main(depth):
    """ Collect data from wikipedia pages """
    with open(f"data/urls_depth_{depth}.json", "r") as f:
        dict_urls = dict(json.load(f))

    # store title, text, category and url in a dataframe
    titles = []
    texts = []
    categories = []
    urls = []
    for category in tqdm(dict_urls.keys(), total=len(dict_urls.keys()), desc="Categories"):
        print(f"Collecting data for category: {category}")
        urls_for_category = dict_urls[category][:5]
        for url in tqdm(urls_for_category, total=len(urls_for_category), desc="Urls"):
            title, text = get_raw_data(url)
            if title and text:
                titles.append(title)
                texts.append(text)
                categories.append(category)
                urls.append(url)
            else:
                print(f"Failed for url: {url}. Not enough data is collected.")
    # save data
    data = pd.DataFrame({"title": titles, "text": texts, "category": categories, "url": urls})
    data.to_csv(f"data/wiki_data_depth_{depth}.csv", index=False, sep=";")


if __name__ == "__main__":

    # Test funktion
    #title, text  = get_raw_data('https://da.wikipedia.org/wiki/Beatles')
    #print(title, text[:100])


    # get depth argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", help="depth of scraping", type=int)
    args = parser.parse_args()
    depth = args.depth if args.depth else None
    if not depth:
        raise ValueError("Please specify depth of scraping")

    main(depth)