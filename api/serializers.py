# import serializer from rest_framework
from rest_framework import serializers

# import model from models.py
from .models import BqResults

# Create a model serializer
class BqSerializer(serializers.ModelSerializer):
	# specify model and fields
	class Meta:
		model = BqResults
		fields = ['store_id', 'timezone_str']


