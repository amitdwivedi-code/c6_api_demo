from rest_framework import serializers
from .models import *


class DescriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descriptions
        fields = '__all__'

class DescriptionsAnotherSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescriptionsProjectandPolicies
        fields = '__all__'