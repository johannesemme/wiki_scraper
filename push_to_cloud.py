import boto3
from botocore.session import Session
from dotenv import load_dotenv
import argparse
import os
import pandas as pd
from tqdm import tqdm

def store_data_in_parquet(depth: int):
    data_path = f"data/wiki_depth_{depth}"
    
    titles = []
    texts = []
    categories = []
    urls = []
    for category in tqdm(os.listdir(data_path), desc="Loading data"):
        for file in os.listdir(f"{data_path}/{category}"):
            with open(f"{data_path}/{category}/{file}", "r", encoding="utf-8") as f:
                text_file = f.read()
            try:
                titles.append(text_file.split("\t")[0])
                urls.append(text_file.split("\t")[1])
                categories.append(text_file.split("\t")[2])
                texts.append(text_file.split("\t")[3])
            except:
                print(f"Error in file {file} in category {category}")

    # check if data file already exists - if so, ask if user wants to overwrite
    file_path = f"data/wiki_depth_{depth}.parquet"
    try:
        pd.read_parquet(file_path)
        overwrite = input(f"File 'wiki_depth_{depth}.parquet' already exists locally. Do you want to overwrite the file? (y/n): ")
        try:
            assert overwrite.lower() == "y"
            pass
        except:
            print("Exiting...")
            return
    except:
        pass

    # store data in parquet file
    data = pd.DataFrame({"title": titles, "text": texts, "category": categories, "url": urls})
    data.to_parquet(f"data/wiki_depth_{depth}.parquet")


        


def push_data_to_s3(
    input_file: str,
    bucket_name: str,
    local_folder: str,
    s3_folder: str
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
        file_path = f"{local_folder}/{input_file}" # local file path
        object_key = f"{s3_folder}/{input_file}" # s3 file path
        try:
            s3.head_object(Bucket=bucket_name, Key=object_key)
            overwrite = input(f"File '{input_file}' already exists on s3. Do you want to overwrite the file? (y/n): ")
            try:
                assert overwrite.lower() == "y"
                pass
            except:
                print("Exiting...")
                return
        except:
            pass
    except:
        print(f"Failed to upload file '{input_file}' to s3")
        pass
        
    # Upload file to s3
    file_path = f"{local_folder}/{input_file}" # local file path
    object_key = f"{s3_folder}/{input_file}" # s3 file path
    s3.upload_file(file_path, bucket_name, object_key) 
    print(f"Uploaded file '{input_file}' to s3 bucket '{bucket_name}' in folder '{s3_folder}'")


if __name__ == "__main__":
    # load arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", help="name of input file", type=str)
    parser.add_argument("--bucket_name", help="name of s3 bucket", type=str)
    parser.add_argument("--s3_folder", help="name of s3 folder", type=str)
    args = parser.parse_args()

    store_data_in_parquet(depth = args.depth)

    push_data_to_s3(
        input_file = f"wiki_depth_{args.depth}.parquet",
        bucket_name = args.bucket_name,
        local_folder = "data",
        s3_folder = args.s3_folder
    )