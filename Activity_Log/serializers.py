from rest_framework import serializers
from .models import *


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity_Log
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format Last_Update field
        if instance.Last_Update:
            data['Last_Update'] = instance.Last_Update.strftime("%d/%m/%Y, %I:%M %p")
        return data

class BRS_Report_LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BRS_Report_Log
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format Last_Update field
        if instance.Last_Update:
            data['Last_Update'] = instance.Last_Update.strftime("%d/%m/%Y, %I:%M %p")
        return data