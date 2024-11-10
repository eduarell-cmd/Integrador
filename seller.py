from google.cloud import storage

def upload_image(file, filename):
    client = storage.Client()
    bucket = client.bucket('farm-to-table-st')
    blob = bucket.blob(filename)
    blob.upload_from_file(file)
    return blob.public.url