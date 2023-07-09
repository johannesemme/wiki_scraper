import boto3
from botocore.session import Session
from dotenv import load_dotenv
import os

def push_data_to_s3(
    input_files: list,
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
        print(f"Uploaded file '{file}' to s3")


if __name__ == "__main__":
    load_dotenv()

    push_data_to_s3(
        input_files=["wikidata_depth_3_cleaned.csv"],
        bucket_name=os.getenv("BUCKET_NAME"),
        local_folder="../data",
        s3_folder=os.getenv("S3_FOLDER")
    )