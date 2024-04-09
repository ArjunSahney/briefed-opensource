from google.cloud import storage

def upload_mp3_file(bucket_name, mp3_file):
    # Initialize the Google Cloud Storage client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Get the file name from the file path
    file_name = mp3_file.split('/')[-1]

    # Create a blob (object) in the bucket
    blob = bucket.blob(file_name)

    # Upload the file to the blob
    blob.upload_from_filename(mp3_file)

    # Make the blob publicly accessible
    blob.make_public()

    # Get the public URL of the file
    public_url = blob.public_url

    return public_url

# Example usage
# bucket_name = 'briefed_mvp2_mp3'
# mp3_file = 'audio/Daniel Liu.mp3'

# public_url = upload_mp3_file(bucket_name, mp3_file)

# # Print the public URL of the uploaded file
# print(public_url)