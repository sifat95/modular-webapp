from django.shortcuts import render

from modular_django.billing.views import check_billing_status
from .models import TableData
from ..billing.models import APILimit
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpResponse
import os
import json
import urllib.request
from PIL import Image
import subprocess
import base64
import uuid
from .utils import *
from .services import APIConnector, TableExtractor
import io

# Create your views here.
@swagger_auto_schema(method='GET',tags=['Give a valid id'])
@csrf_exempt
@api_view(['GET'])
def get_table_data(request, id):
    try:
        data = TableData.objects.get(pk=id)

        data_dict = model_to_dict(data)

        return HttpResponse(json.dumps(data_dict), content_type="application/json")
    except Exception as e:
        print(e)
        return HttpResponse("id: %s not found" % id)

@swagger_auto_schema(method='GET')
@csrf_exempt
@api_view(['GET'])
def get_all_table_data(request):
    try:
        datas = TableData.objects.all()
        data_dicts = [model_to_dict(data) for data in datas]
        return HttpResponse(json.dumps(data_dicts), content_type="application/json")
    except Exception as e:
        print(e)
        return HttpResponse("id: %s not found")

@swagger_auto_schema(method='GET')
@csrf_exempt
@api_view(['GET'])
def get_access_token(request):
    try:
        data =subprocess.getstatusoutput("gcloud auth application-default print-access-token")
        response = {"token": data[1]}
        return HttpResponse(json.dumps(response), content_type="application/json")
    except Exception as e:
        print(e)
        return HttpResponse("id: %s not found")

@swagger_auto_schema(method='POST',tags=['Give a valid image URL'], request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'image': openapi.Schema(type=openapi.TYPE_STRING), 'extractor': openapi.Schema(type=openapi.TYPE_STRING)}))
@csrf_exempt
@api_view(['POST'])
def extract_table(request):
    """Parse a form"""
    input_uri =""
    file_name = ""
    api_limit, billing_status = check_billing_status()

    if request.method=='POST':
        img_base64 = request.data.get("image")
        extractor_client = request.data.get("extractor")
        hospital_profile = request.data.get("hospital_profile")

        imgdata = "data:image/jpeg;base64" + img_base64
        im = TableExtractor.base64_to_image(imgdata)

        im.save("temp.tiff", 'TIFF')
        if(os.path.isfile('temp.jpg')):
            os.remove('temp.jpg')

        rgb_im = im.convert('RGB')
        filename = str(uuid.uuid4()) + ".jpg"
        rgb_im.save(filename)
        
        if(upload_to_bucket("temp",'temp.tiff',"report_ocr").status_code==200):
            input_uri = f"gs://report_ocr/temp"

    if not billing_status:
        return HttpResponse("API LIMIT")
    else:
        extractor_client = APIConnector().getModel(extractor_client)
        result = extractor_client.extractor(input_uri, hospital_profile, filename)
        
        if result!=None and str(result.status_code) == "200":
            api_limit.limit = api_limit.limit + 1
            table_data = result.content.decode('utf-8')
            table_entry = TableData(image_uri = str(imgdata), table_data_str = table_data)
            table_entry.save()
            api_limit.save()
    
        return result
    