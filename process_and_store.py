import html2text
import re
from multiprocessing import Pool
from tqdm import tqdm
import pandas as pd
import argparse
import boto3
from dotenv import load_dotenv
from botocore.session import Session
import os

# https://github.com/Alir3z4/html2text/blob/master/docs/usage.md
h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_emphasis = True
h.ignore_images = True
h.ignore_tables = True
h.body_width = 0
h.unicode_snob = True
h.skip_internal_links = True

def clean_html(raw_text: str):
    """ 
    Cleans text for html tags 
    
    Args:
        raw_text (str): Raw text with html tags
    
    Returns:
        str: Cleaned text
    """
    t = h.handle(raw_text) # convert html to text
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
    return t.strip()

def push_data_to_s3(
    input_files: list,
    bucket_name: str,
    local_folder: str = "data/processed",
    s3_folder: str = "model-job-category",
):
    # Create a Boto3 session
    session = Session()

    # Load AWS credentials from the .aws file
    session_credentials = session.get_credentials()

    # Access the access key ID and secret access key
    aws_access_key_id = session_credentials.access_key
    aws_secret_access_key = session_credentials.secret_key

    # Create an S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)



    # check if files exist on s3 - if so, ask if user wants to overwrite
    try:
        for file in input_files:
            file_path = f"{local_folder}/{file}" # local file path
            object_key = f"{s3_folder}/{file}" # s3 file path
            try:
                s3.head_object(Bucket=bucket_name, Key=object_key)
                overwrite = input(f"File '{file}' already exists on s3. Do you want to overwrite the file? (y/n): ")
                try:
                    assert overwrite.lower() == "y"
                    pass
                except:
                    print("Exiting...")
                    return
            except:
                pass
    except:
        print(f"Failed to upload file '{file}' to s3")
        pass
        

    # Upload files
    for file in input_files:
        file_path = f"{local_folder}/{file}" # local file path
        object_key = f"{s3_folder}/{file}" # s3 file path
        s3.upload_file(file_path, bucket_name, object_key) 



def main(depth: int):
    """ Main function for processing and storing wiki data  """

    # load wiki data pandas
    data = pd.read_csv(f"data/wiki_data_depth_{depth}.csv", sep=";")
    print(data.head())

    # clean text using multiprocessing
    with Pool(8) as p:
        cleaned_text = list(tqdm(p.imap(clean_html, data["text"]), total=len(data["text"]), desc="Cleaning text"))

    # store cleaned text in pandas
    data["text"] = cleaned_text

    # store cleaned data in csv
    data.to_csv(f"data/wiki_data_depth_{depth}_cleaned.csv", sep=";", index=False)
    
    # store data on s3 aws
    push_data_to_s3(
        input_files=[f"wiki_data_depth_{depth}_cleaned.csv"],
        bucket_name="joej-wikipedia",
        local_folder="data",
        s3_folder="scraped-data",
    )





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