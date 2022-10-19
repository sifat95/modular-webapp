from django.shortcuts import render
from .models import APILimit
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import *
from services import BillingInterface
# Create your views here.
# @swagger_auto_schema(method='GET',tags=['Check API Limit Status'])
# @csrf_exempt
# @api_view(['GET'])
def check_billing_status():#(request):

    """Check Billing Status based on API Limit"""

    api_limit = APILimit.objects.all()
    if not api_limit:
        limit_init  = APILimit(limit = 0)
        limit_init.save()
        api_limit = limit_init
    else:
        api_limit = api_limit[0]

    return api_limit, BillingInterface.check_limit(api_limit)

