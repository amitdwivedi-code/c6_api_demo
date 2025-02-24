from rest_framework import serializers
from .models import *


class BRSPolicy1Serializer(serializers.ModelSerializer):
    class Meta:
        model = BRS_Policy_1
        fields = '__all__'
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert the Description field into a list of strings
        if representation.get('Model_Name') == "Web_Link_Policies" and representation.get('Description'):
            representation['Description'] = representation['Description'].split(', ')
        return representation    


class BRSPolicy1aSerializer(serializers.ModelSerializer):
    class Meta:
        model = BRS_Policy_1a
        fields = '__all__'
        
        
class BRSPolicy2Serializer(serializers.ModelSerializer):
    class Meta:
        model = BRS_Policy_2
        fields = '__all__'        