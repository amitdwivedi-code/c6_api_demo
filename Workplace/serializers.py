from rest_framework import serializers
from .models import *

"""
****************************************************************************
Serializer for Workforce
****************************************************************************
"""
class EmployeesSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = '__all__'

    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(
            parent_type="Employees",
            parent_id=obj.id
        )
        return AttachmentSerializer(attachments, many=True).data

class Differently_Abled_EmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Differently_Abled_Employees
        fields = '__all__'

class WorkersSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField()
    class Meta:
        model = Workers
        fields = '__all__'
        
    def get_attachments(self, obj):
        attachments = Attachment.objects.filter(
            parent_type="Workers",
            parent_id=obj.id
        )
        return AttachmentSerializer(attachments, many=True).data


class Differently_Abled_WorkersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Differently_Abled_Workers
        fields = '__all__'

class Workers_Membership_In_Association_Or_UnionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workers_Membership_In_Association_Or_Unions
        fields = '__all__'

class Management_Board_of_DirectorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Management_Board_of_Directors
        fields = '__all__'


class Key_Management_PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Key_Management_Personnel
        fields = '__all__'

class EmployeeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSummary
        fields = '__all__'

    


class Employees_Membership_In_AssociationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employees_Membership_In_Association_Or_Unions
        fields = '__all__'


class Wages_PaidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wages_Paid
        fields = '__all__'



class Median_Remuneration_Salary_WagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Median_Remuneration_Salary_Wages
        fields = '__all__'



class WorkerSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerSummary
        fields = '__all__'


"""
Serializer for Employee Turnover Rate
"""
class Employee_Turnover_RateSerializer(serializers.ModelSerializer):
    # Total_Employee_Turnover_Rate = serializers.FloatField()  # Explicitly using FloatField
    class Meta:
        model = Employee_Turnover_Rate
        fields = '__all__'

"""
Serializer for Workers Turnover Rate
"""
class Workers_Turnover_RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workers_Turnover_Rate
        fields = '__all__'

class Gross_Wages_PaidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gross_Wages_Paid
        fields = '__all__'


class Job_Creation_In_Smaller_TownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Creation_In_Smaller_Town
        fields = '__all__'


"""
****************************************************************************
Serializer for training app
****************************************************************************
"""


class IngeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingeneral
        fields = '__all__'


class OnSkillUpgradationSerializer(serializers.ModelSerializer):
    class Meta:
        model = On_Skill_Upgradation
        fields = '__all__'



class PerformanceAndCareerReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance_And_Career_Reviews
        fields = '__all__'



class AwarenessProgrammesOnESGSerializer(serializers.ModelSerializer):
    class Meta:
        model = Awareness_Programmes_On_ESG
        fields = '__all__'


class OnHealthAndSafetyMeasuresSerializer(serializers.ModelSerializer):
    class Meta:
        model = On_Health_And_Safety_Measures
        fields = '__all__'


class OnHumanRightsIssuesAndPoliciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = On_Human_Rights_Issues_And_Policies
        fields = '__all__'


"""
****************************************************************************
Serializer for health and sefty
****************************************************************************
"""

class PercentageCoveredInWellbeingMeasuresSerializer(serializers.ModelSerializer):

    class Meta:
        model = Percentage_Covered_In_Wellbeing_Measures
        fields ='__all__'




class RetirementBenefitsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Retirement_Benefits
        fields = '__all__'

    
    
class PostPaternalLeaveForPermanentEmployeeAndWorkerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post_Paternal_Leave_For_Permanent_Employee_And_Worker
        fields ='__all__'


class LostTimeInjuryFrequencyRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lost_Time_Injury_Frequency_Rate
        fields ='__all__'


        

class TotalWorkRelatedInjuriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Total_Work_Related_Injuries
        fields ='__all__'

class NoOfFatalitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = No_Of_Fatalities
        fields ='__all__'

        
class InjuryOrIllHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Injury_Or_Ill_Health
        fields ='__all__'

        

class SufferedHighConsequenceWorkRelatedInjurySerializer(serializers.ModelSerializer):
    class Meta:
        model = Suffered_High_Consequence_Work_Related_Injury
        fields ='__all__'


class AssessmentOfPlantsAndOfficesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment_Of_Plants_And_Offices_Health_And_Safety
        fields ='__all__'

        

class AssessmentOfValueChainPartnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment_Of_Value_Chain_Partners_Health_And_Safety
        fields ='__all__'




class Receive_And_Redress_Grievance_MechanismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receive_And_Redress_Grievance_Mechanism
        fields ='__all__'

class CostIncurredOnWellbeingMeasuresSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostIncurredOnWellbeingMeasures
        fields = '__all__'


"""
Gravaence app serializers
"""

class HealthandSafetyComplaintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Health_and_safety_related_complaints
        fields = '__all__'


class HumanRightsComplaintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Human_Rights_related_complaints
        fields = '__all__'


class ConflictsofInterestComplaintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conflict_of_interest_complaints
        fields = '__all__'        


class ReceiveRedressGrievancesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receive_and_redress_grievances_mechanism
        fields = '__all__'



"""
Serializer for policy and penelty
"""


class Policy_Details_Health_safetySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy_Details_Health_safety
        fields = '__all__'

   

class Policy_Details_Human_RightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy_Details_Human_Rights
        fields = '__all__'


class Policy_Details_PenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy_Details_Penalty
        fields = '__all__'






class Assessment_of_plants_and_officesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment_of_plants_and_offices_Policies_and_Penalties
        fields = '__all__'


class Assessment_of_value_chain_partnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment_of_value_chain_partners_Policies_and_Penalties
        fields = '__all__'


class Penalty_MonetarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Penalty_Monetary
        fields = '__all__'


class Penalty_Non_MonetarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Penalty_Non_Monetary
        fields = '__all__'
        

class Details_of_the_appealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details_of_the_appeal
        fields = '__all__'


class Disciplinary_Action_Against_For_curruptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disciplinary_Action_Against_For_curruption
        fields = '__all__'
        

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = "__all__"
