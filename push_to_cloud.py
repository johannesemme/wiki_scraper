import boto3
from botocore.session import Session
from dotenv import load_dotenv
import argparse

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
    print(f"Uploaded file '{input_file}' to s3")


if __name__ == "__main__":
    # load arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help="name of input file", type=str)
    parser.add_argument("--bucket_name", help="name of s3 bucket", type=str)
    parser.add_argument("--s3_folder", help="name of s3 folder", type=str)
    args = parser.parse_args()


    load_dotenv()

    push_data_to_s3(
        input_file = args.input_file,
        bucket_name = args.bucket_name,
        local_folder = "data",
        s3_folder = args.s3_folder
    )