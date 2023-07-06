from bs4 import BeautifulSoup
import requests
import json
import argparse
from tqdm import tqdm

def get_urls(url, type_):
    """ Get urls for either subcategories or pages given a category url """
    main_url = "https://da.wikipedia.org"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    url_list = []
    if type_ == "subcategories":
        try:
            data = soup.findAll('div',attrs={'id':'mw-' + type_})
            for tag in data[0].find_all("a"):
                url_list.append(main_url + tag.attrs["href"])
            return url_list
        except:
            return []
    elif type_ == "pages":
        try:
            data = soup.findAll('div',attrs={'id':'mw-' + type_})
            for tag in data[0].find_all("a"):
                page_name = tag.attrs["href"]
                if not "Bruger:" in page_name and not "Portal:" in page_name:
                  url_list.append(main_url + page_name)
            return url_list
        except:
            return []
        
def main(url_list, url_dict, depth):

    categories = list(url_dict.keys())

    # loop through categories
    for url,category in tqdm(zip(url_list, categories), total=len(url_list)):
        # keep track of page and subcategory urls
        page_urls = []
        subcategory_urls = [[url]] # for each layer we have a list of subcategory urls

        for layer in range(depth):
            sub_categories_in_layer = [] # storage of subcategory urls in the given layer
            for url in subcategory_urls[layer]:
                page_urls.extend(get_urls(url, "pages")) # get page urls
                sub_categories_in_layer.extend(get_urls(url, "subcategories")) # get subcategory urls
            subcategory_urls.append(sub_categories_in_layer)
            
        # store urls for the category
        url_dict[category] = page_urls

    # print number of urls for each category
    for cat in categories:
        print(cat + ":", len(url_dict[cat]))

    print("Total number of urls:", sum([len(url_dict[cat]) for cat in categories]))

    with open(f"data/urls_depth_{depth}.json", "w") as f:
        json.dump(url_dict, f, indent=4)


if __name__ == "__main__":

    # get depth argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", help="depth of scraping", type=int)
    args = parser.parse_args()
    depth = args.depth if args.depth else None
    if not depth:
        raise ValueError("Please specify depth of scraping")

    url_list = [
        "https://da.wikipedia.org/wiki/Kategori:Uddannelse",
        "https://da.wikipedia.org/wiki/Kategori:Samfund",
        "https://da.wikipedia.org/wiki/Kategori:Videnskab",
        "https://da.wikipedia.org/wiki/Kategori:Natur",
        "https://da.wikipedia.org/wiki/Kategori:Teknologi",
        "https://da.wikipedia.org/wiki/Kategori:Kultur",
        "https://da.wikipedia.org/wiki/Kategori:Historie",
        "https://da.wikipedia.org/wiki/Kategori:Sundhed",
        "https://da.wikipedia.org/wiki/Kategori:Geografi",
        "https://da.wikipedia.org/wiki/Kategori:%C3%98konomi",
        "https://da.wikipedia.org/wiki/Kategori:Sport",
        "https://da.wikipedia.org/wiki/Kategori:Religion",
        "https://da.wikipedia.org/wiki/Kategori:Politik",
        "https://da.wikipedia.org/wiki/Kategori:Erhvervsliv"
    ]
        

    # Dictionary 
    url_dict = {"Uddannelse" : [],
        "Samfund": [],
        "Videnskab": [],
        "Natur": [],
        "Teknologi": [],
        "Kultur": [],
        "Historie": [],
        "Sundhed": [],
        "Geografi": [],
        "Økonomi": [],
        "Sport": [],
        "Religion": [],
        "Politik": [],
        "Erhvervsliv": []}
    
    main(url_list, url_dict, depth)