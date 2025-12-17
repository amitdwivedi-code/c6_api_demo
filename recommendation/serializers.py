from rest_framework import serializers
from .models import RecommendationModel,SOPDocument

class RecommendationSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecommendationModel
        fields = ['id', 'recommendation_key', 'recommendation_value', 'financial_year']
        extra_kwargs = {
            'recommendation_key': {'required': True, 'allow_blank': False},
            'Financial_Year': {'required': True, 'allow_blank': False},
        }
        

class SOPDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOPDocument
        fields = [
            # 'id',
            'name',
            'description',
            'file',
            'uploaded_by',
            'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'updated_at']
