from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    location =  serializers.ListField(child=serializers.CharField())
    class Meta:
        model = User
        fields = '__all__'

class EmployeeCodeSerializer(serializers.Serializer):
    employee_code = serializers.CharField()
    
class EmployeeNameSerializer(serializers.Serializer):
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    
class EmployeeCodeNameSerializer(serializers.Serializer):
    employee_code = serializers.CharField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()

class Access_ControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Access_Control
        fields = '__all__'

class Finance_Access_ControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finance_Access_Control
        fields = '__all__'

class Company_Secretary_Access_ControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company_Secretary_Access_Control
        fields = '__all__'

class Human_Resoursce_Access_ControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Human_Resoursce_Access_Control
        fields = '__all__'


class EmployeesAccessControlSerializer(serializers.ModelSerializer):
    role = serializers.ListField(child=serializers.CharField(), required=True)
    permissions = serializers.ListField(child=serializers.CharField(), required=True)

    class Meta:
        model = EmployeesAccessControl
        fields = '__all__'
        extra_kwargs = {
            'employee_code': {'required': True, 'max_length': 255},
            'employee_name': {'required': True, 'max_length': 255},
            'role': {'required': True, 'error_messages': {'required': 'Role field is mandatory and cannot be empty.'}},
            'section': {'required': True, 'max_length': 255, 'trim_whitespace': True},
            'page': {'required': True, 'max_length': 255, 'trim_whitespace': True},
            'sub_page': {'required': True, 'max_length': 255, 'trim_whitespace': True},
            'permissions': {'required': True, 'error_messages': {'required': 'permissions field is mandatory and cannot be empty.'}},
        }
        
    def validate_permissions(self, value):
        allowed_permissions = {'add', 'edit', 'delete', 'view'}
        for val in value:
            if val not in allowed_permissions:
                raise serializers.ValidationError(f"Permissions array cannot contain invalid string {val} select choice {list(allowed_permissions)}")

        if not isinstance(value, list):
            raise serializers.ValidationError("Permissions must be an array.")
        
        return value
    
    def validate_role(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Role must be an array.")
        
        if not value:
            raise serializers.ValidationError("Role array cannot be empty.")
        
        return value