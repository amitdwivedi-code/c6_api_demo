from rest_framework import serializers
from .models import *


class EnergyAssessmentbyExternalAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Energy_Assessment_by_External_Agency
        fields = '__all__'



class ElectricityConsumptionmwhSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electricity_Consumption_mwh
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['Unit']:  # Check if 'Unit' exists
            data['Unit'] = "MWh"  # Always return 'MWh' in the API response
        return data 



class ElectricityConsumptionGJSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electricity_Consumption_GJ
        fields = '__all__'



class FuelConsumptionOnsiteCombustionGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fuel_Consumption_Onsite_Combustion_General
        fields = '__all__'



class FuelConsumptionOnsiteCombustionGJSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fuel_Consumption_Onsite_Combustion_GJ
        fields = '__all__'



class FuelConsumptionOnsiteVehiclesGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fuel_Consumption_Onsite_Vehicles_General
        fields = '__all__'



class FuelConsumptionOnsiteVehiclesGJSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fuel_Consumption_Onsite_Vehicles_GJ
        fields = '__all__'



class InboundLogisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbound_Logistics
        fields = '__all__'


class OutboundLogisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outbound_Logistics
        fields = '__all__'



class BusinessTravelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business_Travel
        fields = '__all__'



class EmployeeCommutingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee_Commuting
        fields = '__all__'



class EnergyIntensitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Energy_Intensity
        fields = '__all__'


class EnergyIntensityforProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Energy_Intensity_for_Production
        fields = '__all__'



class EnergyConsumptionOtherSourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Energy_Consumption_Other_Sources
        fields = '__all__'



class ProcessEmissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process_Emissions
        fields = '__all__'



class RefrigerantLossesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refrigerant_Losses
        fields = '__all__'

######################################## life cycle  #######################################

class LifeCyclePerspectiveAssessmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Life_Cycle_Perspective_Assessments
        fields = '__all__'



class ConcernsandActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concerns_and_Action
        fields = '__all__'



class MaterialBusinessConductIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material_Business_Conduct_Issue
        fields = '__all__'



class SustainableSourcingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sustainable_Sourcing
        fields = '__all__'



class RecycledorReusedInputMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recycled_or_Reused_Input_Material
        fields = '__all__'



class ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        fields = '__all__'



class EndofLifeofProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = End_of_Life_of_Product
        fields = '__all__'



class ReclaimedProductsandPackagingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reclaimed_Products_and_Packaging
        fields = '__all__'



class ReclaimProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reclaim_Process
        fields = '__all__'



# ################################## Emmission ##############################################################

class Scope1EmissionsbyFacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope1_Emissions_by_Facilities
        fields = '__all__'


class Scope1EmissionsbyFuelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope1_Emissions_by_Fuel
        fields = '__all__'


class Scope1EmissionsbyGHGTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope1_Emissions_by_GHG_Type
        fields = '__all__'


class Scope1IntensitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope1_Intensity
        fields = '__all__'



class Scope2EmissionsbyFacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope2_Emissions_by_Facilities
        fields = '__all__'


class Scope2EmissionsbyFuelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope2_Emissions_by_Fuel
        fields = '__all__'


class Scope2EmissionsbyGHGTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope2_Emissions_by_GHG_Type
        fields = '__all__'



class Scope2IntensitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope2_Intensity
        fields = '__all__'


class EmissionAssessmentByExternalAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Emission_Assessment_By_External_Agency
        fields = '__all__'


class Scope3EmissionsbyFacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope3_Emissions_by_Facilities
        fields = '__all__'


class Scope3EmissionsbyActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope3_Emissions_by_Activity
        fields = '__all__'


class Scope3EmissionsbyGHGTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope3_Emissions_by_GHG_Type
        fields = '__all__'


class Scope3IntensitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope3_Intensity
        fields = '__all__'        



class EmissionFactorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionFactors
        fields = '__all__'
# ################################## Water And Air #######################################

class WaterAssessmentbyExternalAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Water_Assessment_By_External_Agency
        fields = '__all__'



class WaterIntensitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Water_Intensity
        fields = '__all__'

class WaterStressAreasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water_Stress_Areas
        fields = '__all__'


class WaterWithdrawalBySourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water_withdrawal_By_Source
        fields = '__all__'


class WaterConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water_Consumption
        fields = '__all__'

class Water_Discharge_To_Destination_Without_TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water_Discharge_To_Destination_Without_Treatment
        fields = '__all__'        


class Water_Discharge_To_Destination_With_TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water_Discharge_To_Destination_With_Treatment
        fields = '__all__'        


class Air_Emissions_Other_Than_GHG_EmissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Air_Emissions_Other_Than_GHG_Emissions
        fields = '__all__'
                
###########################################    Waste     ##########################################################



class WasteAssessmentbyExternalAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste_Assessment_By_External_Agency
        fields = '__all__'

class WasteGeneratedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste_Generated
        fields = '__all__'       


class WasteRecoveredSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste_Recovered
        fields = '__all__'

         

class WasteDisposedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste_Disposed
        fields = '__all__'



class WasteIntensitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste_Intensity
        fields = '__all__'

#############################################  Sustainability    ########################################################

class PercentageOfRandDandCapexInvestmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Percentage_Of_R_and_D_and_Capex_Investments
        fields = "__all__"


class OperationsInEcologicallySensitiveAreasSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Operations_In_Ecologically_Sensitive_Areas
        fields = "__all__"


class EnvironmentalImpactAssessmentsOfProjectsUndertakenSerializer(serializers.ModelSerializer):
    Date = serializers.DateField(
        format="%d-%m-%Y",  
        input_formats=["%Y-%m-%d", "%d-%m-%Y"]  # Allow both formats
    )    
    class Meta:
        model = Environmental_Impact_Assessments_Of_Projects_Undertaken
        fields = "__all__"


class NonComplianceWithTheApplicableEnvironmentalLawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Non_Compliance_With_The_Applicable_Environmental_Law
        fields = "__all__"


class  InitiativesTowardsCarbonZeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Initiatives_Towards_Carbon_Zero
        fields = "__all__"               

