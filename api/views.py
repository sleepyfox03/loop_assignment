# Import necessary modules and functions
from django.shortcuts import render


# import viewsets
from rest_framework import viewsets
from datetime import datetime
from uuid import uuid4
from .serializers import BqSerializer
from .models import BqResults,Reports,StoreStatus
from rest_framework.decorators import action
from rest_framework.response import Response
# Import a custom task for generating reports .This tasks.py contains functions for our logic
from .tasks import generate_report
from django.conf import settings

import os 
from django.http import FileResponse, HttpResponse,JsonResponse
# Create a viewset for handling reports
class ReportViewSet(viewsets.ModelViewSet):
	# Define the queryset to retrieve all BqResults objects
	queryset = BqResults.objects.all()
	
	# Specify the serializer to be used for serialization
	serializer_class = BqSerializer

	 
	@action(detail=False, methods=['get'])
	def trigger_report(self, request):
		'''
		 This view action generates a random string ID using uuid4 (random UUID),creates a new report 
		 with a "running" status, and initiates the report generation.
		'''
		report_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(uuid4())
		Reports.objects.create(report_id = report_id,status = "Running")
		generate_report(report_id)
		return Response({'report_id': report_id})
	
	@action(detail=False, methods=['get'],url_path=r'get_report/(?P<id>[-\w]+)')
	
	def get_report(self, request,id=None):
	 	# Retrieve the report object by its ID
		a = Reports.objects.get(report_id = id)
		# Define the CSV file path
		csv_file_path = './static/' +id +".csv"
    	# Check if the csv file exists
		if os.path.exists(csv_file_path):
		    # If the file exists, generate a URL for it and mark the status as completed
			file_path = "localhost:8000/static/" + id + ".csv"
			return Response({"csv_file":file_path,"status":"Completed"})
				
		# If the file doesn't exist, provide the report ID and mark the status as "Running"
		return Response({"report id":a.report_id,"status":"Running"})
	 
	 
 
 
 