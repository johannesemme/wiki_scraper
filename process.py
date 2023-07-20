import html2text
import re
from multiprocessing import Pool
from tqdm import tqdm
import pandas as pd
import argparse
import os

# https://github.com/Alir3z4/html2text/blob/master/docs/usage.md
h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_emphasis = True
h.ignore_images = True
h.ignore_tables = True
h.body_width = 0
h.unicode_snob = True
h.single_line_break = True

def clean_html(raw_text: str):
    """ 
    Cleans text for html tags 
    
    Args:
        raw_text (str): Raw text with html tags
    
    Returns:
        str: Cleaned text
    """
    t = h.handle(raw_text) # convert html to text
    res = re.findall(r'\"(.+?)\"', t) # find all text inside quotes
    for r in res: # remove unnescessary spaces inside quotes like: " text " --> "text"
        t = t.replace(r, f"{r.strip()}")
    t = re.sub(" +", " ",t).strip() # remove trailing spaces
    t = re.sub(r' ([.,;:?!)}\]])', r'\1', t) # remove spaces before punctuations and brackets
    t = t.replace("*", "").strip() # remove bullet points
    t = re.sub(r'\[.*?\]', '', t) # remove all inside [] - used for editing wikipage texts (like: [ redigér | rediger kildetekst] ) + marking links (like: [4])
    t = re.sub(r'#', '', t) # avoid #'s that mark headers

    lines = [t.strip() for t in t.split("\n")] # obtain a list of lines
    chunks = []
    curr_chunk = ""
    for l in lines: # combine lines into text chunks - discard empty lines
        if "Hentet fra" in l:
            continue
        if len(l)>0:
            # add punctuations where missing
            l = l if l[-1] in [":", ";", "!", "?", "."] else l + "." 
            curr_chunk += " " + l
        else:
            if len(curr_chunk)>0:
                chunks.append(curr_chunk.strip())
            curr_chunk = ""
    if len(curr_chunk)>0: # add last text chunk
        chunks.append(curr_chunk)
    t = " ".join(chunks )
    t = t.replace("\xad", "") # remove soft hyphens (https://en.wikipedia.org/wiki/Soft_hyphen
    t = t.replace("\xa0", " ") # replace non-breaking space (https://en.wikipedia.org/wiki/Non-breaking_space)
    t = t.replace("\u200b", "") # remove zero width space (https://en.wikipedia.org/wiki/Zero-width_space)
    t = t.replace("\\", "")
    #t = re.sub(" +", " ",t).strip() # remove trailing spaces
    return t.strip()

def clean_title(raw_title: str):
    """ 
    Cleans text for html tags 
    
    Args:
        raw_title (str): Raw title with html tags
    
    Returns:
        str: Cleaned title
    """
    t = h.handle(raw_title) 
    t = t.replace("_", " ") 
    t = re.sub(" +", " ",t).strip() # remove trailing spaces
    return t.strip()


def main(depth: int):
    """ Main function for processing and storing wiki data  """

    # inside wiki_{depth} there are subfolders with categories. Each of these have a bunch of txt files
    # load all txt files into a pandas dataframe

    data_path = f"data/wiki_depth_{depth}"
    
    titles = []
    texts = []
    categories = []
    urls = []
    for category in tqdm(os.listdir(data_path), desc="Loading data"):
        for file in os.listdir(f"{data_path}/{category}"):
            with open(f"{data_path}/{category}/{file}", "r", encoding="utf-8") as f:
                text_file = f.read()
            # get title, text, category and url from text_file (stored using .write(title + "\t" + url + "\t" + category + "\t" + text + "\n"))
            try:
                titles.append(text_file.split("\t")[0])
                urls.append(text_file.split("\t")[1])
                categories.append(text_file.split("\t")[2])
                texts.append(text_file.split("\t")[3])
            except:
                print(f"Error in file {file} in category {category}")

    data = pd.DataFrame({"title": titles, "text": texts, "category": categories, "url": urls})


    # clean text using multiprocessing
    with Pool(8) as p:
        cleaned_text = list(tqdm(p.imap(clean_html, data["text"]), total=len(data["text"]), desc="Cleaning text"))
    # clean title using multiprocessing
    with Pool(8) as p:
        cleaned_title = list(tqdm(p.imap(clean_title, data["title"]), total=len(data["title"]), desc="Cleaning title"))

    # store cleaned text in pandas
    data["text"] = cleaned_text
    data["title"] = cleaned_title
    print(data.head())

    # store cleaned data in parquet format
    data.to_parquet(f"data/wiki_depth_{depth}.parquet")

if __name__ == "__main__":

    # get depth argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", help="depth of scraping", type=int)
    args = parser.parse_args()
    depth = args.depth if args.depth else 3

    main(depth)