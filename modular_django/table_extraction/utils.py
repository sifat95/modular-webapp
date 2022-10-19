import os
from pprint import pprint
from google.cloud import storage
from rest_framework import status
from rest_framework.response import Response
from pathlib import Path
from django.templatetags.static import static

BASE_DIR = Path(__file__).resolve().parent.parent
credentials= str(BASE_DIR)+str(static('json/bs-bl-291005-69953c8429ef.json'))
auth_credential = os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

storage_client = storage.Client()
bucket_name = "report_ocr"  #Replace with actual bucket name
bucket = storage_client.bucket(bucket_name)

def upload_to_bucket(blob_name:str, file_path:str, bucket_name:str):
    '''
    Upload file to a bucket
    : blob_name  (str) - object name
    : file_path (str)
    : bucket_name (str)
    '''
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    return Response(blob_name, status=status.HTTP_200_OK)


def blobIsExits(blob_name:str, bucket_name:str):
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if(blob.exists()):
        return True
    else:
        return False


def delete_from_bucket(blob_name:str,file_path:str,bucket_name:str):
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if(blob.exists()):
        blob.delete()
    else:
        return Response(blob_name, status=status.HTTP_404_NOT_FOUND)
    return Response(blob_name, status=status.HTTP_200_OK)