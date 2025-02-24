from rest_framework import serializers
from .models import *


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company_Profile
        fields = '__all__'



class TurnoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turnover
        fields = '__all__'



class NetworthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Networth
        fields = '__all__'



class BusinessActivityDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business_Activity_Details
        fields = '__all__'



class ProductsServicesDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products_Services_Details
        fields = '__all__'



class ExportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exports
        fields = '__all__'



class BusinessActivityTurnoverSerializer(serializers.Serializer):
    Business_Activity = serializers.CharField(max_length=200)
    Percent_Turnover = serializers.FloatField()


class BusinessActivitySerializer(serializers.ModelSerializer):

    Business_Activity_and_Turnover = BusinessActivityTurnoverSerializer(many=True)
    class Meta:
        model = Business_Activity
        fields = '__all__'



class ProductsServicesTurnoverSerializer(serializers.Serializer):
    Product_Service = serializers.CharField(max_length=200)
    Percent_Turnover = serializers.FloatField()


class ProductsServicesSerializer(serializers.ModelSerializer):

    Products_Services_and_Turnover = ProductsServicesTurnoverSerializer(many=True)
    class Meta:
        model = Products_Services
        fields = '__all__'


class OfficesandPlantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offices_and_Plants
        fields = '__all__'



class MarketsServedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Markets_Served
        fields = '__all__'



class PaidupCapitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paid_up_Capital
        fields = '__all__'



class HoldingsSerializer(serializers.ModelSerializer):
    Type_of_Holding = serializers.CharField(max_length=200, allow_blank=True)
    class Meta:
        model = Holdings
        fields = '__all__'



class FacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facilities
        fields = '__all__'

class CompanyLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company_Profile
        fields = '__all__'

   
class NumberOfDaysOfAccountsPayablesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberOfDaysOfAccountsPayablesModel
        fields = '__all__'

class Concentration_Of_SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concentration_Of_Sales
        fields = '__all__'


class Concentration_Of_PurchasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concentration_Of_Purchases
        fields = '__all__'


class ShareOfRPTsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareOfRPTs
        fields = '__all__'


class Indian_States_CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indian_States_Cities
        fields =  '__all__'