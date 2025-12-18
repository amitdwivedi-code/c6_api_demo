from rest_framework import serializers
from .models import RecommendationModel

class RecommendationSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecommendationModel
        fields = ['id', 'recommendation_key', 'recommendation_value', 'financial_year']
        extra_kwargs = {
            'recommendation_key': {'required': True, 'allow_blank': False},
            'Financial_Year': {'required': True, 'allow_blank': False},
        }
        