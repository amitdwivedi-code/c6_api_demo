from rest_framework import serializers
from .models import *




class ListStakeholderGroupsSerializer(serializers.ModelSerializer):
    Channels_Of_Communication = serializers.CharField(max_length=50000, allow_blank=True)
    Frequency_Of_Engagement = serializers.CharField(max_length=50000, allow_blank=True)

    class Meta:
        model = List_Stakeholder_Groups
        fields = '__all__'

        
class NumberOfAffiliationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Number_Of_Affiliations
        fields = '__all__'
  

class Top10TradeAndIndustryChambersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Top_10_Trade_And_Industry_Chambers
        fields = '__all__'


class DetailsOfAnyIssuesRelatedToAntiCompetitiveConductByTheEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity
        fields = '__all__'


class DetailsOfPublicPolicyPositionsAdvocatedByTheEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Details_Of_Public_Policy_Positions_Advocated_By_The_Entity
        fields = '__all__'


class AwarenessProgrammesForValueChainPartnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Awareness_Programmes_For_Value_Chain_Partners
        fields = '__all__'
        

class Information_on_CSR_ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information_on_CSR_Projects
        fields = '__all__'

class Benefits_Derived_And_Shared_From_Intellectual_PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefits_Derived_And_Shared_From_Intellectual_Property
        fields = '__all__'        

class Details_Of_Intellectual_Property_Related_DisputesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details_Of_Intellectual_Property_Related_Disputes
        fields = '__all__'                

class Details_Of_Beneficiaries_Of_CSR_ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details_Of_Beneficiaries_Of_CSR_Projects
        fields = '__all__'          


class Turnover_Of_Products_As_A_Percentage_Of_TurnoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turnover_Of_Products_As_A_Percentage_Of_Turnover
        fields = '__all__'    



class Number_of_Consumer_ComplaintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Number_of_Consumer_Complaints
        fields = '__all__'                             

class Details_Of_Instances_Of_Product_RecallsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details_Of_Instances_Of_Product_Recalls
        fields = '__all__'              

class Corporate_Social_Responsibility_DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporate_Social_Responsibility_Details
        fields = '__all__' 


class Consumer_DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Consumer_Details
        fields = '__all__'                

class Stakeholders_DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stakeholders_Details
        fields = '__all__' 


class Society_DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Society_Details
        fields = '__all__'            


class DetailsOfActionsTakenToMitigateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details_Of_Actions_Taken_To_Mitigate
        fields = '__all__'              



class PercentageOfInputMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Percentage_Of_Input_Material
        fields = '__all__' 


        

class OngoingRehabilitationAndResettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ongoing_Rehabilitation_And_Resettlement
        fields = '__all__' 

        
class DetailsOfSocialImpactAssessmentsSerializer(serializers.ModelSerializer):
    Date_Of_Notification = serializers.DateField(format="%d-%m-%Y", input_formats=["%Y-%m-%d", "%d-%m-%Y"])
    class Meta:
        model = Details_Of_Social_Impact_Assessments
        fields = '__all__' 

   
        
class TransparencyAndDisclosureCompliancesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransparencyAndDisclosureCompliancesModel
        fields = '__all__' 

class Number_Of_Instance_Of_Data_BreacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Number_Of_Instance_Of_Data_Breache
        fields = '__all__'