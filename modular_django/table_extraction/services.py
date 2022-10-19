import os
import json
from pickle import NONE
from spellchecker import SpellChecker

from google.cloud import vision
from google.cloud import documentai_v1beta2 as documentai

from django.templatetags.static import static
from pathlib import Path

from PIL import Image
from google.protobuf.json_format import MessageToJson
from .utils import *

import base64
import uuid
import io

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

class ModelAPIInterface:
    def __init__(self):
        self.spell = SpellChecker()
    
    def extractor(self, image):
        pass
    def set_credentials(self):
        pass

class HospitalTableTemplate:
    def __init__(self, hospital, document, report_keyword):
        self.hospital = hospital
        self.document = document
        self.report_keyword = report_keyword


    def _get_text(self, el):
        """Convert text offset indexes into text snippets."""
        response = ""
        # If a text segment spans several lines, it will
        # be stored in different text segments.
        for segment in el.text_anchor.text_segments:
            start_index = segment.start_index
            end_index = segment.end_index
            response += self.document.text[start_index:end_index]
        return response

    def _get_text_column(self, el, index):
        """Convert text offset indexes into text snippets."""
        response = ""
        # If a text segment spans several lines, it will
        # be stored in different text segments.
        for segment in el.text_anchor.text_segments:
            start_index = segment.start_index
            end_index = segment.end_index
            response += self.document.text[start_index:end_index]
        return {"header": response.strip(), "accessorKey": str(index)}

    def hospital_table_extractor(self, hospital_table):
        """Extract hospital table data."""
        table_column = []

        table_body = []

        for row_num, row in enumerate(hospital_table):
            column_counter = 0
            temp_row = {}

            for idx, cell in enumerate(row.cells):
                temp_column = {}
                item = self._get_text(cell.layout).strip()
                
                if item in self.report_keyword:
                    temp_column["header"] = item
                    temp_column["accessorKey"] = str(column_counter)
                    table_column.append(temp_column)
                    column_counter += 1
                else:
                    temp_row[str(idx)] = item
                    if len(table_column) - 1 == idx:
                        table_body.append(temp_row)

        return {"specific_table": True, "table": {"table_column": table_column, "table_body": table_body}}
    
    def map_data_to_template(self, table_data,):
        # pass
        if self.hospital == 'POPULAR':
            print(table_data)
            hospital_column = []
            table_info = []
            hospital_body = []

            table_body = []
            for row_num, row in enumerate(table_data.header_rows):
                table_column = [self._get_text_column(cell.layout, idx) for idx, cell in enumerate(row.cells)]
                print(table_column)
                    
            hospital_table = False

            for column in table_column:
                if (column["header"] in self.report_keyword):
                    hospital_table = True
                    hospital_column = table_column
                    break

            if hospital_table:
                # Extract hospital table if header have column
                for row_num, row in enumerate(table_data.body_rows):
                    temp_dic = {}
                    for idx, cell in enumerate(row.cells):
                        temp_dic[str(idx)] = self._get_text(cell.layout)
                    hospital_body.append(temp_dic)
                table_response= {"table_column": hospital_column, "table_body": hospital_body}
                response = [table_response]
                return response
                # return HttpResponse(json.dumps(response), content_type="application/json")
            else:
                # Extract hospital table if body have header
                for row_num, row in enumerate(table_data.body_rows):
                    cells = "\t".join([self._get_text(cell.layout) for cell in row.cells])
                    temp_dic = {}
                    for idx, cell in enumerate(row.cells):
                        item = self._get_text(cell.layout).strip()

                        if hospital_table == False and  item in self.report_keyword:
                            hospital_data = self.hospital_table_extractor(table.body_rows)
                            print(hospital_data)
                            if hospital_data["specific_table"]:
                                table_data = hospital_data["table"]
                                table_response= {"table_column": table_data["table_column"], "table_body": table_data["table_body"]}
                                response = [table_response]
                                return response
                                
                temp_dic[str(idx)] = item
                table_body.append(temp_dic)
                table_info.append("Row {}: {}".format(row_num, cells))
                
                table_response= {"table_column": table_column, "table_body": table_body}
                response.append(table_response)
                return response


class GCPDocumentsAI(ModelAPIInterface):
    def __init__(self):
        ModelAPIInterface.__init__(self)
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.client = documentai.DocumentUnderstandingServiceClient()
        self.project_id= ''

    def set_credentials(self):

        credentials = str(self.BASE_DIR)+str(static('json/bs-bl-291005-69953c8429ef.json'))
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

    def get_table_bound_hints(self):
        # Improve table parsing results by providing bounding boxes
        # specifying where the box appears in the document (optional)
        return [
            documentai.types.TableBoundHint(
                page_number=1,
                bounding_box=documentai.types.BoundingPoly(
                    # Define a polygon around tables to detect
                    # Each vertice coordinate must be a number between 0 and 1
                    normalized_vertices=[
                        # Top left
                        documentai.types.geometry.NormalizedVertex(x=0, y=0),
                        # Top right
                        documentai.types.geometry.NormalizedVertex(x=1, y=0),
                        # Bottom right
                        documentai.types.geometry.NormalizedVertex(x=1, y=1),
                        # Bottom left
                        documentai.types.geometry.NormalizedVertex(x=0, y=1),
                    ]
                ),
            )
        ]
    
    def api_request_config(self, input_uri):
        gcs_source = documentai.types.GcsSource(uri=input_uri)

        # mime_type can be application/pdf, image/tiff,
        # and image/gif, or application/json
        input_config = documentai.types.InputConfig(
            gcs_source=gcs_source, mime_type="image/tiff"
        )

        # Setting enabled=True enables form extraction
        table_extraction_params = documentai.types.TableExtractionParams(
            enabled=True, table_bound_hints=self.get_table_bound_hints()
        )

        # Location can be 'us' or 'eu'
        parent = "projects/{}/locations/us".format(self.project_id)
        return documentai.types.ProcessDocumentRequest(
            parent=parent,
            input_config=input_config,
            table_extraction_params=table_extraction_params,
        )

    def extractor(self, input_uri, hospital_profile, filename):
        
        def _get_text(el):
            """Convert text offset indexes into text snippets."""
            response = ""
            # If a text segment spans several lines, it will
            # be stored in different text segments.
            for segment in el.text_anchor.text_segments:
                start_index = segment.start_index
                end_index = segment.end_index
                response += document.text[start_index:end_index]
            return response

        def _get_text_column(el, index):
            """Convert text offset indexes into text snippets."""
            response = ""
            # If a text segment spans several lines, it will
            # be stored in different text segments.
            for segment in el.text_anchor.text_segments:
                start_index = segment.start_index
                end_index = segment.end_index
                response += document.text[start_index:end_index]
            return {"header": response.strip(), "accessorKey": str(index)}

        
        document = self.client.process_document(request=self.api_request_config(input_uri))
        
        if(blobIsExits("temp", "report_ocr")):
            try:
                if(os.path.isfile('temp.tiff')):
                    os.remove('temp.tiff')
                res = delete_from_bucket("temp","temp.tiff","report_ocr")
            except:
                print(res)
        
        
        response=[]
        page_number =""

        suggested_colomn_header = []
        POPULAR = "POPULAR DIAGNOSTIC CENTRE LTD."
        LABAID1 = "LABAID DIAGNOSTIC"
        LABAID2 = "LAB\nAID\nLTD\n"

        ocr_text = document.text
        # print(f"ocr_text: {ocr_text}")
        if ocr_text.find(POPULAR) != -1:
            suggested_colomn_header = ["Test Name", "Result", "Unit", "Reference Range"]

        elif (ocr_text.find(LABAID1) != -1) or (ocr_text.find(LABAID2) != -1):
            suggested_colomn_header = ["Test", "Result", "Reference Value"]

        for page in document.pages:
            table_column = []
            # print("Page number: {}".format(page.page_number))
            for table_num, table in enumerate(page.tables):
                # Extract rows from the table
                table_info = []
                table_body = []

                # Extract table header
                for row_num, row in enumerate(table.header_rows):
                    for idx, cell in enumerate(row.cells):
                        item =  _get_text(cell.layout)

                        if item.split("\n")[0] in suggested_colomn_header:
                            hospital_profile = "hospital"
                            break

                if hospital_profile != "hospital":
                    # Extract table body
                    # Extract body if no header found
                    for row_num, row in enumerate(table.body_rows):

                        for idx, cell in enumerate(row.cells):
                            item =  _get_text(cell.layout)
                            # print(item)
                            if item.split("\n")[0] in suggested_colomn_header:
                                hospital_profile = "hospital"
                                break

                if hospital_profile == "hospital":
                  
                    popular_table = HospitalTableTemplate(hospital="POPULAR", document=document, report_keyword=suggested_colomn_header).map_data_to_template(table)
                
                    return HttpResponse(json.dumps(popular_table), content_type="application/json")
                    
        if hospital_profile == "default": 
            for page in document.pages:
                table_column = []
                
                for table_num, table in enumerate(page.tables):
                    table_info = []
                    table_body = []
                    for row_num, row in enumerate(table.header_rows):
                        table_column = [_get_text_column(cell.layout, idx) for idx, cell in enumerate(row.cells)]

                    for row_num, row in enumerate(table.body_rows):
                        temp_dic = {}
                        for idx, cell in enumerate(row.cells):
                            temp_dic[str(idx)] = _get_text(cell.layout)
                        table_body.append(temp_dic)

                    table_response= {"table_column": table_column, "table_body": table_body}
                    response.append(table_response)

            return HttpResponse(json.dumps(response), content_type="application/json")

class AzureFormRec(ModelAPIInterface):
    def __init__(self):
        ModelAPIInterface.__init__(self)
        #self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.endpoint = ""
        self.key = ""
        self.document_analysis_client = DocumentAnalysisClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
    
    def extractor(self, input_uri, hospital_profile, filename):
        #"https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"

        # create your `DocumentAnalysisClient` instance and `AzureKeyCredential` variable
        im = Image.open(filename)

        img_byte_arr = io.BytesIO()
        im.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        poller = self.document_analysis_client.begin_analyze_document(
                "prebuilt-document", img_byte_arr)
        result = poller.result()

        response = []

        for table_idx, table in enumerate(result.tables):
            col=[]
            dt=[]

            for cell in table.cells:
                c=cell
                if(cell.content=='BIOCHEMISTRY'):
                    targetrow= cell.row_index

            for cell in table.cells:    
                if(cell.row_index==0):
                    c=cell.content
                    col.append(c)
                elif(cell.row_index!=targetrow):
                    d=cell.content
                    dt.append(d)
            
            #splitting in dictionaries
            col_len=len(col)
            col_name=[]

            for i in range(col_len):
                tempdict1={}
                
                tempdict1["accessorKey"]=col[i]
                tempdict1["header"]=col[i]
                col_name.append(tempdict1)

            #for data values

            dt_len=len(dt)
            data = []

            for i in range(0, dt_len, col_len):  
                tempdict2={} 
                for j in range(col_len):
        
                    if((i+j)>=dt_len):v='null'
                    else: v=dt[i+j]
                    
                    k= col[j]
                    tempdict2[k]=v
                
                data.append(tempdict2)

            table_response= {"table_column": col_name, "table_body": data}
            response.append(table_response)

            return HttpResponse(json.dumps(response), content_type="application/json")

class APIConnector:
    def __init__(self):
        pass
    def getModel(self, extractor_client):
        if extractor_client=='GCP':
            return GCPDocumentsAI()
        elif extractor_client=='AzureForm':
            return AzureFormRec()
    
class TableExtractor(ModelAPIInterface):
    def __init__(self):
        pass
    def get_accuracy(self):
        return

    def base64_to_image(img_base64):
        imgdata = base64.b64decode(img_base64)
        return Image.open(io.BytesIO(imgdata))