# from .models import Business_Travel, Electricity_Consumption_GJ, Electricity_Consumption_mwh, EmissionFactors, Employee_Commuting, Fuel_Consumption_Onsite_Combustion_GJ, Fuel_Consumption_Onsite_Combustion_General, Fuel_Consumption_Onsite_Vehicles_General, Inbound_Logistics, Outbound_Logistics, Production, Scope1_Emissions_by_Facilities, Scope2_Emissions_by_Facilities, Scope3_Emissions_by_Facilities, Waste_Generated, Water_Consumption
from CompanyDetails.models import *

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from bson import Decimal128
from decimal import Decimal, DivisionByZero
from .models import *

def get_conversion_factor(fuel_type, unit):
    if fuel_type == "Diesel" and unit == "Litre":
        return 0.0386
    elif fuel_type == "Petrol" and unit == "Litre":
        return 0.0342
    elif fuel_type == "Natural Gas (NG)" and unit == "Kg":
        return 0.0555
    elif fuel_type == "Natural Gas (NG)" and unit == "MBtu(Million British Thermal Units) of Gas (Energy Basis)":
        return 1.05506
    elif fuel_type == "Natural Gas (NG)" and unit == "m3 of Gas(Volume Basis)":
        return 0.0358
    elif fuel_type == "LPG" and unit == "Kg":
        return 0.0461
    elif fuel_type == "Coal-All Type" and unit == "Kg":
        return 0.024
    elif fuel_type == "Biomas-Wood/Wood Waste" and unit == "Kg":
        return 0.019
    elif fuel_type == "Biomas-Primary Solid Biomass" and unit == "Kg":
        return 0.016
    elif fuel_type == "Biomas-Bio Gasoline" and unit == "Kg of Bio Gasoline":
        return 0.044
    elif fuel_type == "Biomas-Bio Diesel" and unit == "Kg of Bio Diesel":
        return 0.038
    elif fuel_type == "EV" and unit == "kWh":
        return 0.0036
    elif fuel_type == "Methanol" and unit == "m3":
        return 15.6
    elif fuel_type == "Furnace Oil" and unit == "litre":
        return 2.75
    elif fuel_type == "L D O" and unit == "litre":
        return 0
    elif fuel_type == "Liquid Nitrogen" and unit == "m3":
        return 0
    elif fuel_type == "Liquid Oxygen" and unit == "m3":
        return 0
    elif fuel_type == "LSHS" and unit == "kls":
        return 0
    elif fuel_type == "PNG Q&T" and unit == "SCM":
        return 0
    elif fuel_type == "PNG RTHF" and unit == "SCM":
        return 0
    elif fuel_type == "Wood" and unit == "Kg":
        return 0.019


def calculate_energy_intensity():
    # import pdb; pdb.set_trace()
    from .models import Fuel_Consumption_Onsite_Combustion_GJ
    from CompanyDetails.models import Turnover
    fuel_combustion_FY = Fuel_Consumption_Onsite_Combustion_GJ.objects.values('Financial_Year').distinct()
    fuel_combustion_FY_list = [record['Financial_Year'] for record in fuel_combustion_FY]

    # Query for distinct financial years
    from .models import Electricity_Consumption_GJ
    electricity_FY = Electricity_Consumption_GJ.objects.values('Financial_Year').distinct()
    electricity_FY_list = [record['Financial_Year'] for record in electricity_FY]

    # Query for distinct financial years
    turnover_FY = Turnover.objects.values('Financial_Year').distinct()
    turnover_FY_list = [record['Financial_Year'] for record in turnover_FY]

    combined_list = fuel_combustion_FY_list.copy()
    combined_list.extend(electricity_FY_list)
    combined_list.extend(turnover_FY_list)

    FY_List = list(set(combined_list))

    # sorted_financial_years = sorted(FY_List, key=lambda x: int(x[2:]), reverse=True)

    energy_intensity = []
    for year in FY_List:
        energy_intensity_dict = {}
        
        ############################ Fuel Consumption #################################
        
        fuel_combustion_filter = Fuel_Consumption_Onsite_Combustion_GJ.objects.filter(Financial_Year=year)
        fuel_consumption_apr = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Apr
                fuel_consumption_apr += float(decimal_value.to_decimal())

        fuel_consumption_may = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_May
                fuel_consumption_may += float(decimal_value.to_decimal())

        fuel_consumption_jun = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Jun
                fuel_consumption_jun += float(decimal_value.to_decimal())

        
        fuel_consumption_jul = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Jul
                fuel_consumption_jul += float(decimal_value.to_decimal())


        fuel_consumption_aug = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Aug
                fuel_consumption_aug += float(decimal_value.to_decimal())

        fuel_consumption_sep = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Sep
                fuel_consumption_sep += float(decimal_value.to_decimal())

        
        fuel_consumption_oct = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Oct
                fuel_consumption_oct += float(decimal_value.to_decimal())


        fuel_consumption_nov = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Nov
                fuel_consumption_nov += float(decimal_value.to_decimal())


        fuel_consumption_dec = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Dec
                fuel_consumption_dec += float(decimal_value.to_decimal())


        fuel_consumption_jan = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Jan
                fuel_consumption_jan += float(decimal_value.to_decimal())


        fuel_consumption_feb = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Feb
                fuel_consumption_feb += float(decimal_value.to_decimal())

        
        fuel_consumption_mar = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Mar
                fuel_consumption_mar += float(decimal_value.to_decimal())

        
        ############################ Electricity Consumption #################################

        electricity_filter = Electricity_Consumption_GJ.objects.filter(Financial_Year=year)
        electricity_consumption_apr = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Apr
                electricity_consumption_apr += float(decimal_value.to_decimal())

        electricity_consumption_may = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_May
                electricity_consumption_may += float(decimal_value.to_decimal())

        
        electricity_consumption_jun = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Jun
                electricity_consumption_jun += float(decimal_value.to_decimal())


        electricity_consumption_jul = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Jul
                electricity_consumption_jul += float(decimal_value.to_decimal())

        
        electricity_consumption_aug = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Aug
                electricity_consumption_aug += float(decimal_value.to_decimal())

        

        electricity_consumption_sep = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Sep
                electricity_consumption_sep += float(decimal_value.to_decimal())


        electricity_consumption_oct = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Oct
                electricity_consumption_oct += float(decimal_value.to_decimal())


        electricity_consumption_nov = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Nov
                electricity_consumption_nov += float(decimal_value.to_decimal())


        electricity_consumption_dec = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Dec
                electricity_consumption_dec += float(decimal_value.to_decimal())

        
        electricity_consumption_jan = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Jan
                electricity_consumption_jan += float(decimal_value.to_decimal())


        electricity_consumption_feb = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Feb
                electricity_consumption_feb += float(decimal_value.to_decimal())

        
        electricity_consumption_mar = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Mar
                electricity_consumption_mar += float(decimal_value.to_decimal())


        ############################ Turnover #################################

        turnover_filter = Turnover.objects.filter(Financial_Year=year)
        turnover_apr = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Apr
                turnover_apr += float(decimal_value.to_decimal())

        turnover_may = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_May
                turnover_may += float(decimal_value.to_decimal())

        
        turnover_jun = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Jun
                turnover_jun += float(decimal_value.to_decimal())

        
        turnover_jul = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Jul
                turnover_jul += float(decimal_value.to_decimal())

        
        turnover_aug = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Aug
                turnover_aug += float(decimal_value.to_decimal())

        
        turnover_sep = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Sep
                turnover_sep += float(decimal_value.to_decimal())

        
        turnover_oct = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Oct
                turnover_oct += float(decimal_value.to_decimal())


        turnover_nov = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Nov
                turnover_nov += float(decimal_value.to_decimal())


        turnover_dec = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Dec
                turnover_dec += float(decimal_value.to_decimal())


        turnover_jan = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Jan
                turnover_jan += float(decimal_value.to_decimal())


        turnover_feb = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Feb
                turnover_feb += float(decimal_value.to_decimal())


        turnover_mar = 0.0
        if turnover_filter:
            for data in turnover_filter:
                decimal_value = data.Turnover_Mar
                turnover_mar += float(decimal_value.to_decimal())
        
        #################################### Energy Intensity ####################################3
        
        energy_intensity_apr = 0.0
        if turnover_apr <= 0:
            energy_intensity_apr = 0.0
        else:
            energy_intensity_apr = round((fuel_consumption_apr + electricity_consumption_apr) / turnover_apr, 2)

        energy_intensity_may = 0.0
        if turnover_may <= 0:
            energy_intensity_may = 0.0
        else:
            energy_intensity_may = round((fuel_consumption_may + electricity_consumption_may) / turnover_may, 2)


        energy_intensity_jun = 0.0
        if turnover_jun <= 0:
            energy_intensity_jun = 0.0
        else:
            energy_intensity_jun = round((fuel_consumption_jun + electricity_consumption_jun) / turnover_jun, 2)

        
        energy_intensity_jul = 0.0
        if turnover_jul <= 0:
            energy_intensity_jul = 0.0
        else:
            energy_intensity_jul = round((fuel_consumption_jul + electricity_consumption_jul) / turnover_jul, 2)


        energy_intensity_aug = 0.0
        if turnover_aug <= 0:
            energy_intensity_aug = 0.0
        else:
            energy_intensity_aug = round((fuel_consumption_aug + electricity_consumption_aug) / turnover_aug, 2)


        energy_intensity_sep = 0.0
        if turnover_sep <= 0:
            energy_intensity_sep = 0.0
        else:
            energy_intensity_sep = round((fuel_consumption_sep + electricity_consumption_sep) / turnover_sep, 2)


        energy_intensity_oct = 0.0
        if turnover_oct <= 0:
            energy_intensity_oct = 0.0
        else:
            energy_intensity_oct = round((fuel_consumption_oct + electricity_consumption_oct) / turnover_oct, 2)


        energy_intensity_nov = 0.0
        if turnover_nov <= 0:
            energy_intensity_nov = 0.0
        else:
            energy_intensity_nov = round((fuel_consumption_nov + electricity_consumption_nov) / turnover_nov, 2)


        energy_intensity_dec = 0.0
        if turnover_dec <= 0:
            energy_intensity_dec = 0.0
        else:
            energy_intensity_dec = round((fuel_consumption_dec + electricity_consumption_dec) / turnover_dec, 2)


        energy_intensity_jan = 0.0
        if turnover_jan <= 0:
            energy_intensity_jan = 0.0
        else:
            energy_intensity_jan = round((fuel_consumption_jan + electricity_consumption_jan) / turnover_jan, 2)


        energy_intensity_feb = 0.0
        if turnover_feb <= 0:
            energy_intensity_feb = 0.0
        else:
            energy_intensity_feb = round((fuel_consumption_feb + electricity_consumption_feb) / turnover_feb, 2)


        energy_intensity_mar = 0.0
        if turnover_mar <= 0:
            energy_intensity_mar = 0.0
        else:
            energy_intensity_mar = round((fuel_consumption_mar + electricity_consumption_mar) / turnover_mar, 2)

        ##################################################################################################3

        energy_intensity_dict["Financial_Year"] = year
        energy_intensity_dict["Energy_Intensity_Apr"] = energy_intensity_apr
        energy_intensity_dict["Energy_Intensity_May"] = energy_intensity_may
        energy_intensity_dict["Energy_Intensity_Jun"] = energy_intensity_jun
        energy_intensity_dict["Energy_Intensity_Jul"] = energy_intensity_jul
        energy_intensity_dict["Energy_Intensity_Aug"] = energy_intensity_aug
        energy_intensity_dict["Energy_Intensity_Sep"] = energy_intensity_sep
        energy_intensity_dict["Energy_Intensity_Oct"] = energy_intensity_oct
        energy_intensity_dict["Energy_Intensity_Nov"] = energy_intensity_nov
        energy_intensity_dict["Energy_Intensity_Dec"] = energy_intensity_dec
        energy_intensity_dict["Energy_Intensity_Jan"] = energy_intensity_jan
        energy_intensity_dict["Energy_Intensity_Feb"] = energy_intensity_feb
        energy_intensity_dict["Energy_Intensity_Mar"] = energy_intensity_mar
        energy_intensity_dict["Total_Energy_Intensity"] = round(energy_intensity_apr + energy_intensity_may + energy_intensity_jun + energy_intensity_jul + energy_intensity_aug + energy_intensity_sep + energy_intensity_oct + energy_intensity_nov + energy_intensity_dec + energy_intensity_jan + energy_intensity_feb + energy_intensity_mar, 2)
        energy_intensity.append(energy_intensity_dict)       

    return energy_intensity



def get_months():
    all_months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # Slice the list to start with April and then add the months before April to the end
    months_starting_with_april = all_months[3:] + all_months[:3]
    
    return months_starting_with_april


def calculate_energy_intensity_for_production():
    # import pdb;pdb.set_trace()
    from .models import Fuel_Consumption_Onsite_Combustion_GJ
    fuel_combustion_FY = Fuel_Consumption_Onsite_Combustion_GJ.objects.values('Financial_Year').distinct()
    fuel_combustion_FY_list = [record['Financial_Year'] for record in fuel_combustion_FY]

    # Query for distinct financial years
    from .models import Electricity_Consumption_GJ
    electricity_FY = Electricity_Consumption_GJ.objects.values('Financial_Year').distinct()
    electricity_FY_list = [record['Financial_Year'] for record in electricity_FY]

    # Query for distinct financial years
    from .models import Production
    production_FY = Production.objects.values('Financial_Year').distinct()
    production_FY_list = [record['Financial_Year'] for record in production_FY]

    combined_list = fuel_combustion_FY_list.copy()
    combined_list.extend(electricity_FY_list)
    combined_list.extend(production_FY_list)

    FY_List = list(set(combined_list))

    sorted_financial_years = sorted(FY_List, key=lambda x: int(x[2:].split('-')[0]), reverse=True)

    energy_intensity = []
    for year in sorted_financial_years:
        energy_intensity_dict = {}
        
        ############################ Fuel Consumption #################################
        
        fuel_combustion_filter = Fuel_Consumption_Onsite_Combustion_GJ.objects.filter(Financial_Year=year)
        fuel_consumption_apr = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Apr
                fuel_consumption_apr += float(decimal_value.to_decimal())

        fuel_consumption_may = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_May
                fuel_consumption_may += float(decimal_value.to_decimal())

        fuel_consumption_jun = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Jun
                fuel_consumption_jun += float(decimal_value.to_decimal())

        
        fuel_consumption_jul = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Jul
                fuel_consumption_jul += float(decimal_value.to_decimal())


        fuel_consumption_aug = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Aug
                fuel_consumption_aug += float(decimal_value.to_decimal())

        fuel_consumption_sep = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Sep
                fuel_consumption_sep += float(decimal_value.to_decimal())

        
        fuel_consumption_oct = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Oct
                fuel_consumption_oct += float(decimal_value.to_decimal())


        fuel_consumption_nov = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Nov
                fuel_consumption_nov += float(decimal_value.to_decimal())


        fuel_consumption_dec = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Dec
                fuel_consumption_dec += float(decimal_value.to_decimal())


        fuel_consumption_jan = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Jan
                fuel_consumption_jan += float(decimal_value.to_decimal())


        fuel_consumption_feb = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Feb
                fuel_consumption_feb += float(decimal_value.to_decimal())

        
        fuel_consumption_mar = 0.0
        if fuel_combustion_filter:
            for data in fuel_combustion_filter:
                decimal_value = data.Fuel_Consumption_Mar
                fuel_consumption_mar += float(decimal_value.to_decimal())

        
        ############################ Electricity Consumption #################################

        electricity_filter = Electricity_Consumption_GJ.objects.filter(Financial_Year=year)
        electricity_consumption_apr = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Apr
                electricity_consumption_apr += float(decimal_value.to_decimal())

        electricity_consumption_may = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_May
                electricity_consumption_may += float(decimal_value.to_decimal())

        
        electricity_consumption_jun = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Jun
                electricity_consumption_jun += float(decimal_value.to_decimal())


        electricity_consumption_jul = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Jul
                electricity_consumption_jul += float(decimal_value.to_decimal())

        
        electricity_consumption_aug = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Aug
                electricity_consumption_aug += float(decimal_value.to_decimal())

        

        electricity_consumption_sep = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Sep
                electricity_consumption_sep += float(decimal_value.to_decimal())


        electricity_consumption_oct = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Oct
                electricity_consumption_oct += float(decimal_value.to_decimal())


        electricity_consumption_nov = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Nov
                electricity_consumption_nov += float(decimal_value.to_decimal())


        electricity_consumption_dec = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Dec
                electricity_consumption_dec += float(decimal_value.to_decimal())

        
        electricity_consumption_jan = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Jan
                electricity_consumption_jan += float(decimal_value.to_decimal())


        electricity_consumption_feb = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Feb
                electricity_consumption_feb += float(decimal_value.to_decimal())

        
        electricity_consumption_mar = 0.0
        if electricity_filter:
            for data in electricity_filter:
                decimal_value = data.Electricity_Consumption_Mar
                electricity_consumption_mar += float(decimal_value.to_decimal())


        ############################ Production #################################

        production_filter = Production.objects.filter(Financial_Year=year)
        production_apr = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Apr
                production_apr += float(decimal_value.to_decimal())

        production_may = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_May
                production_may += float(decimal_value.to_decimal())

        production_jun = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Jun
                production_jun += float(decimal_value.to_decimal())

        production_jul = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Jul
                production_jul += float(decimal_value.to_decimal())

        production_aug = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Aug
                production_aug += float(decimal_value.to_decimal())

        production_sep = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Sep
                production_sep += float(decimal_value.to_decimal())

        production_oct = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Oct
                production_oct += float(decimal_value.to_decimal())

        production_nov = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Nov
                production_nov += float(decimal_value.to_decimal())

        production_dec = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Dec
                production_dec += float(decimal_value.to_decimal())

        production_jan = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Jan
                production_jan += float(decimal_value.to_decimal())

        production_feb = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Feb
                production_feb += float(decimal_value.to_decimal())

        production_mar = 0.0
        if production_filter:
            for data in production_filter:
                decimal_value = data.Production_Mar
                production_mar += float(decimal_value.to_decimal())

         #################################### Energy Intensity ####################################3
        
        energy_intensity_apr = 0.0
        if production_apr == 0.0:
            energy_intensity_apr = 0.0
        else:
            energy_intensity_apr = round((fuel_consumption_apr + electricity_consumption_apr) / production_apr, 2)

        energy_intensity_may = 0.0
        if production_may == 0.0:
            energy_intensity_may = 0.0
        else:
            energy_intensity_may = round((fuel_consumption_may + electricity_consumption_may) / production_may, 2)


        energy_intensity_jun = 0.0
        if production_jun == 0.0:
            energy_intensity_jun = 0.0
        else:
            energy_intensity_jun = round((fuel_consumption_jun + electricity_consumption_jun) / production_jun, 2)

        
        energy_intensity_jul = 0.0
        if production_jul == 0.0:
            energy_intensity_jul = 0.0
        else:
            energy_intensity_jul = round((fuel_consumption_jul + electricity_consumption_jul) / production_jul, 2)


        energy_intensity_aug = 0.0
        if production_aug == 0.0:
            energy_intensity_aug = 0.0
        else:
            energy_intensity_aug = round((fuel_consumption_aug + electricity_consumption_aug) / production_aug, 2)


        energy_intensity_sep = 0.0
        if production_sep == 0.0:
            energy_intensity_sep = 0.0
        else:
            energy_intensity_sep = round((fuel_consumption_sep + electricity_consumption_sep) / production_sep, 2)


        energy_intensity_oct = 0.0
        if production_oct == 0.0:
            energy_intensity_oct = 0.0
        else:
            energy_intensity_oct = round((fuel_consumption_oct + electricity_consumption_oct) / production_oct, 2)


        energy_intensity_nov = 0.0
        if production_nov == 0.0:
            energy_intensity_nov = 0.0
        else:
            energy_intensity_nov = round((fuel_consumption_nov + electricity_consumption_nov) / production_nov, 2)


        energy_intensity_dec = 0.0
        if production_dec == 0.0:
            energy_intensity_dec = 0.0
        else:
            energy_intensity_dec = round((fuel_consumption_dec + electricity_consumption_dec) / production_dec, 2)


        energy_intensity_jan = 0.0
        if production_jan == 0.0:
            energy_intensity_jan = 0.0
        else:
            energy_intensity_jan = round((fuel_consumption_jan + electricity_consumption_jan) / production_jan, 2)


        energy_intensity_feb = 0.0
        if production_feb == 0.0:
            energy_intensity_feb = 0.0
        else:
            energy_intensity_feb = round((fuel_consumption_feb + electricity_consumption_feb) / production_feb, 2)


        energy_intensity_mar = 0.0
        if production_mar == 0.0:
            energy_intensity_mar = 0.0
        else:
            energy_intensity_mar = round((fuel_consumption_mar + electricity_consumption_mar) / production_mar, 2)


        ##################################################################################################3

        energy_intensity_dict["Financial_Year"] = year
        energy_intensity_dict["Energy_Intensity_Apr"] = energy_intensity_apr
        energy_intensity_dict["Energy_Intensity_May"] = energy_intensity_may
        energy_intensity_dict["Energy_Intensity_Jun"] = energy_intensity_jun
        energy_intensity_dict["Energy_Intensity_Jul"] = energy_intensity_jul
        energy_intensity_dict["Energy_Intensity_Aug"] = energy_intensity_aug
        energy_intensity_dict["Energy_Intensity_Sep"] = energy_intensity_sep
        energy_intensity_dict["Energy_Intensity_Oct"] = energy_intensity_oct
        energy_intensity_dict["Energy_Intensity_Nov"] = energy_intensity_nov
        energy_intensity_dict["Energy_Intensity_Dec"] = energy_intensity_dec
        energy_intensity_dict["Energy_Intensity_Jan"] = energy_intensity_jan
        energy_intensity_dict["Energy_Intensity_Feb"] = energy_intensity_feb
        energy_intensity_dict["Energy_Intensity_Mar"] = energy_intensity_mar
        energy_intensity_dict["Total_Energy_Intensity"] = round(energy_intensity_apr + energy_intensity_may + energy_intensity_jun + energy_intensity_jul + energy_intensity_aug + energy_intensity_sep + energy_intensity_oct + energy_intensity_nov + energy_intensity_dec + energy_intensity_jan + energy_intensity_feb + energy_intensity_mar, 2)
        energy_intensity.append(energy_intensity_dict)       

    return energy_intensity


######################################## sustainability  #######################################
def custom_url_validator(value):
    validator = URLValidator()
    try:
        # Try to validate the value directly
        validator(value)
    except ValidationError:
        # If it fails, check if it starts with 'www.'
        if value.startswith('www.'):
            # Attempt to validate it by prepending 'http://'
            validator(f'http://{value}')
        else:
            # Raise the original validation error if not
            raise

######################################## Emmissions  #######################################


def calculate_process_emission_co2e_emission(gas_type, quantity):
    from .models import EmissionFactors
    gwp_value = (EmissionFactors.objects.filter(Type_of_Emission='Process Emission', Greenhouse_Gas=gas_type).
                 values_list('Hundred_year_GWP', flat=True).first())
    co2e_emission = round((quantity * gwp_value), 2)

    tco2e_emission = round((co2e_emission / 1000), 2)

    return co2e_emission, tco2e_emission


def calculate_refrigerant_losses_consumption_co2e_emission(refrigerant_type,
                                                                       refrigerant_stock_at_the_start_quantity,
                                                                       refrigerant_stock_at_the_end_quantity,
                                                                       refrigerant_purchased_quantity,
                                                                       refrigerant_to_fill_new_equipment_quantity):
    from .models import EmissionFactors
    sum1 = refrigerant_stock_at_the_start_quantity + refrigerant_purchased_quantity
    sum2 = refrigerant_stock_at_the_end_quantity + refrigerant_to_fill_new_equipment_quantity

    total_refrigerant_consumption = round((sum1 - sum2), 2)

    gwp_value = EmissionFactors.objects.filter(Greenhouse_Gas=refrigerant_type).values_list('Hundred_year_GWP', flat=True).first()

    co2e_emission = round((total_refrigerant_consumption * gwp_value), 2)

    tco2e_emission = round((co2e_emission / 1000), 2)

    return total_refrigerant_consumption, co2e_emission, tco2e_emission



def calculate_scope_1_emissions_fuel_onsite_combustion_1():
    # Get a distinct list of Financial_Year
    from .models import Fuel_Consumption_Onsite_Combustion_General, EmissionFactors
    financial_years = Fuel_Consumption_Onsite_Combustion_General.objects.values_list('Financial_Year', flat=True).distinct()
    financial_years_list = list(financial_years)

    # Get a distinct list of Facilities
    facilities = Fuel_Consumption_Onsite_Combustion_General.objects.values_list('Facility', flat=True).distinct()
    facility_list = list(facilities)

    result = []

    for year in financial_years_list:
        for fac in facility_list:
            record_json = {}
            #breakpoint()
            records = Fuel_Consumption_Onsite_Combustion_General.objects.filter(Financial_Year=year, Facility=fac).values_list('Financial_Year', 'Facility', 'Fuel_Type', 'Unit')
            records_list = list(records)

            if records_list:
                record_json['Financial_Year'] = year
                record_json['Facility'] = fac
                fuel_types = [record[2] for record in records_list]  # Collect Fuel_Types
                units = [record[3] for record in records_list]

                emission_apr = 0.0
                emission_may = 0.0
                emission_jun = 0.0
                emission_jul = 0.0
                emission_aug = 0.0
                emission_sep = 0.0
                emission_oct = 0.0
                emission_nov = 0.0
                emission_dec = 0.0
                emission_jan = 0.0
                emission_feb = 0.0
                emission_mar = 0.0
                for rec1, unit in zip(fuel_types, units):

                    ef = EmissionFactors.objects.get(Type_of_Emission='Fuel', Fuel=rec1, Unit=unit)
                    if ef:
                        ef_apr = ef.CO2E_Emission_Factor

                    apr_records = Fuel_Consumption_Onsite_Combustion_General.objects.filter(Financial_Year=year, Facility=fac, Fuel_Type=rec1)
                    for apr in apr_records:

                        fuel_consumption_apr = apr.Fuel_Consumption_Apr
                        fuel_consumption_may = apr.Fuel_Consumption_May
                        fuel_consumption_jun = apr.Fuel_Consumption_Jun
                        fuel_consumption_jul = apr.Fuel_Consumption_Jul
                        fuel_consumption_aug = apr.Fuel_Consumption_Aug
                        fuel_consumption_sep = apr.Fuel_Consumption_Sep
                        fuel_consumption_oct = apr.Fuel_Consumption_Oct
                        fuel_consumption_nov = apr.Fuel_Consumption_Nov
                        fuel_consumption_dec = apr.Fuel_Consumption_Dec
                        fuel_consumption_jan = apr.Fuel_Consumption_Jan
                        fuel_consumption_feb = apr.Fuel_Consumption_Feb
                        fuel_consumption_mar = apr.Fuel_Consumption_Mar

                        # Convert to Decimal128 for MongoDB
                        ef_apr = Decimal128(str(ef_apr))
                        fuel_consumption_apr = Decimal128(str(fuel_consumption_apr))
                        fuel_consumption_may = Decimal128(str(fuel_consumption_may))
                        fuel_consumption_jun = Decimal128(str(fuel_consumption_jun))
                        fuel_consumption_jul = Decimal128(str(fuel_consumption_jul))
                        fuel_consumption_aug = Decimal128(str(fuel_consumption_aug))
                        fuel_consumption_sep = Decimal128(str(fuel_consumption_sep))
                        fuel_consumption_oct = Decimal128(str(fuel_consumption_oct))
                        fuel_consumption_nov = Decimal128(str(fuel_consumption_nov))
                        fuel_consumption_dec = Decimal128(str(fuel_consumption_dec))
                        fuel_consumption_jan = Decimal128(str(fuel_consumption_jan))
                        fuel_consumption_feb = Decimal128(str(fuel_consumption_feb))
                        fuel_consumption_mar = Decimal128(str(fuel_consumption_mar))

                        # Calculate emissions
                        emission_apr += float(ef_apr.to_decimal()) * float(fuel_consumption_apr.to_decimal())
                        emission_may += float(ef_apr.to_decimal()) * float(fuel_consumption_may.to_decimal())
                        emission_jun += float(ef_apr.to_decimal()) * float(fuel_consumption_jun.to_decimal())
                        emission_jul += float(ef_apr.to_decimal()) * float(fuel_consumption_jul.to_decimal())
                        emission_aug += float(ef_apr.to_decimal()) * float(fuel_consumption_aug.to_decimal())
                        emission_sep += float(ef_apr.to_decimal()) * float(fuel_consumption_sep.to_decimal())
                        emission_oct += float(ef_apr.to_decimal()) * float(fuel_consumption_oct.to_decimal())
                        emission_nov += float(ef_apr.to_decimal()) * float(fuel_consumption_nov.to_decimal())
                        emission_dec += float(ef_apr.to_decimal()) * float(fuel_consumption_dec.to_decimal())
                        emission_jan += float(ef_apr.to_decimal()) * float(fuel_consumption_jan.to_decimal())
                        emission_feb += float(ef_apr.to_decimal()) * float(fuel_consumption_feb.to_decimal())
                        emission_mar += float(ef_apr.to_decimal()) * float(fuel_consumption_mar.to_decimal())

                record_json["Emission_Apr"] = round(emission_apr, 2)
                record_json["Emission_May"] = round(emission_may, 2)
                record_json["Emission_Jun"] = round(emission_jun, 2)
                record_json["Emission_Jul"] = round(emission_jul, 2)
                record_json["Emission_Aug"] = round(emission_aug, 2)
                record_json["Emission_Sep"] = round(emission_sep, 2)
                record_json["Emission_Oct"] = round(emission_oct, 2)
                record_json["Emission_Nov"] = round(emission_nov, 2)
                record_json["Emission_Dec"] = round(emission_dec, 2)
                record_json["Emission_Jan"] = round(emission_jan, 2)
                record_json["Emission_Feb"] = round(emission_feb, 2)
                record_json["Emission_Mar"] = round(emission_mar, 2)
                result.append(record_json)
    
    return result



def calculate_scope_1_emissions_fuel_onsite_vehicles_1():
    # Get a distinct list of Financial_Year
    from .models import Fuel_Consumption_Onsite_Vehicles_General, EmissionFactors
    financial_years = Fuel_Consumption_Onsite_Vehicles_General.objects.values_list('Financial_Year', flat=True).distinct()
    financial_years_list = list(financial_years)

    # Get a distinct list of Facilities
    facilities = Fuel_Consumption_Onsite_Vehicles_General.objects.values_list('Facility', flat=True).distinct()
    facility_list = list(facilities)

    result = []

    for year in financial_years_list:
        for fac in facility_list:
            record_json = {}

            records = Fuel_Consumption_Onsite_Vehicles_General.objects.filter(Q(Financial_Year=year) & Q(Facility=fac) & (Q(Ownership="3rd party owned and company controlled") | Q(Ownership='Company owned and controlled'))).values_list('Financial_Year', 'Facility', 'Fuel_Type', 'Unit')
            records_list = list(records)

            if records_list:
                record_json['Financial_Year'] = year
                record_json['Facility'] = fac
                fuel_types = [record[2] for record in records_list]  # Collect Fuel_Types
                units = [record[3] for record in records_list]

                emission_apr = 0.0
                emission_may = 0.0
                emission_jun = 0.0
                emission_jul = 0.0
                emission_aug = 0.0
                emission_sep = 0.0
                emission_oct = 0.0
                emission_nov = 0.0
                emission_dec = 0.0
                emission_jan = 0.0
                emission_feb = 0.0
                emission_mar = 0.0
                for rec1, unit in zip(fuel_types, units):
                    ef = EmissionFactors.objects.get(Type_of_Emission='Fuel', Fuel=rec1, Unit=unit)
                    if ef:
                        ef_apr = ef.CO2E_Emission_Factor

                    apr_records = Fuel_Consumption_Onsite_Vehicles_General.objects.filter(Financial_Year=year, Facility=fac, Fuel_Type=rec1)
                    for apr in apr_records:

                        fuel_consumption_apr = apr.Fuel_Consumption_Apr
                        fuel_consumption_may = apr.Fuel_Consumption_May
                        fuel_consumption_jun = apr.Fuel_Consumption_Jun
                        fuel_consumption_jul = apr.Fuel_Consumption_Jul
                        fuel_consumption_aug = apr.Fuel_Consumption_Aug
                        fuel_consumption_sep = apr.Fuel_Consumption_Sep
                        fuel_consumption_oct = apr.Fuel_Consumption_Oct
                        fuel_consumption_nov = apr.Fuel_Consumption_Nov
                        fuel_consumption_dec = apr.Fuel_Consumption_Dec
                        fuel_consumption_jan = apr.Fuel_Consumption_Jan
                        fuel_consumption_feb = apr.Fuel_Consumption_Feb
                        fuel_consumption_mar = apr.Fuel_Consumption_Mar

                        # Convert to Decimal128 for MongoDB
                        ef_apr = Decimal128(str(ef_apr))
                        fuel_consumption_apr = Decimal128(str(fuel_consumption_apr))
                        fuel_consumption_may = Decimal128(str(fuel_consumption_may))
                        fuel_consumption_jun = Decimal128(str(fuel_consumption_jun))
                        fuel_consumption_jul = Decimal128(str(fuel_consumption_jul))
                        fuel_consumption_aug = Decimal128(str(fuel_consumption_aug))
                        fuel_consumption_sep = Decimal128(str(fuel_consumption_sep))
                        fuel_consumption_oct = Decimal128(str(fuel_consumption_oct))
                        fuel_consumption_nov = Decimal128(str(fuel_consumption_nov))
                        fuel_consumption_dec = Decimal128(str(fuel_consumption_dec))
                        fuel_consumption_jan = Decimal128(str(fuel_consumption_jan))
                        fuel_consumption_feb = Decimal128(str(fuel_consumption_feb))
                        fuel_consumption_mar = Decimal128(str(fuel_consumption_mar))

                        # Calculate emissions
                        emission_apr += float(ef_apr.to_decimal()) * float(fuel_consumption_apr.to_decimal())
                        emission_may += float(ef_apr.to_decimal()) * float(fuel_consumption_may.to_decimal())
                        emission_jun += float(ef_apr.to_decimal()) * float(fuel_consumption_jun.to_decimal())
                        emission_jul += float(ef_apr.to_decimal()) * float(fuel_consumption_jul.to_decimal())
                        emission_aug += float(ef_apr.to_decimal()) * float(fuel_consumption_aug.to_decimal())
                        emission_sep += float(ef_apr.to_decimal()) * float(fuel_consumption_sep.to_decimal())
                        emission_oct += float(ef_apr.to_decimal()) * float(fuel_consumption_oct.to_decimal())
                        emission_nov += float(ef_apr.to_decimal()) * float(fuel_consumption_nov.to_decimal())
                        emission_dec += float(ef_apr.to_decimal()) * float(fuel_consumption_dec.to_decimal())
                        emission_jan += float(ef_apr.to_decimal()) * float(fuel_consumption_jan.to_decimal())
                        emission_feb += float(ef_apr.to_decimal()) * float(fuel_consumption_feb.to_decimal())
                        emission_mar += float(ef_apr.to_decimal()) * float(fuel_consumption_mar.to_decimal())

                record_json["Emission_Apr"] = round(emission_apr, 2)
                record_json["Emission_May"] = round(emission_may, 2)
                record_json["Emission_Jun"] = round(emission_jun, 2)
                record_json["Emission_Jul"] = round(emission_jul, 2)
                record_json["Emission_Aug"] = round(emission_aug, 2)
                record_json["Emission_Sep"] = round(emission_sep, 2)
                record_json["Emission_Oct"] = round(emission_oct, 2)
                record_json["Emission_Nov"] = round(emission_nov, 2)
                record_json["Emission_Dec"] = round(emission_dec, 2)
                record_json["Emission_Jan"] = round(emission_jan, 2)
                record_json["Emission_Feb"] = round(emission_feb, 2)
                record_json["Emission_Mar"] = round(emission_mar, 2)
                result.append(record_json)
    
    return result


def calculate_scope_1_emissions_by_facilities():
    fuel_onsite_combustion_list = calculate_scope_1_emissions_fuel_onsite_combustion_1()
    fuel_onsite_vehicles_list = calculate_scope_1_emissions_fuel_onsite_vehicles_1()

    combined = {}

    # Process first list
    for item in fuel_onsite_combustion_list:
        year = item["Financial_Year"]
        facility = item["Facility"]
        emission_apr = item["Emission_Apr"]
        emission_may = item["Emission_May"]
        emission_jun = item["Emission_Jun"]
        emission_jul = item["Emission_Jul"]
        emission_aug = item["Emission_Aug"]
        emission_sep = item["Emission_Sep"]
        emission_oct = item["Emission_Oct"]
        emission_nov = item["Emission_Nov"]
        emission_dec = item["Emission_Dec"]
        emission_jan = item["Emission_Jan"]
        emission_feb = item["Emission_Feb"]
        emission_mar = item["Emission_Mar"]

        if year not in combined:
            combined[year] = {}
        if facility in combined[year]:
            combined[year][facility]['Emission_Apr'] += emission_apr
            combined[year][facility]['Emission_May'] += emission_may
            combined[year][facility]['Emission_Jun'] += emission_jun
            combined[year][facility]['Emission_Jul'] += emission_jul
            combined[year][facility]['Emission_Aug'] += emission_aug
            combined[year][facility]['Emission_Sep'] += emission_sep
            combined[year][facility]['Emission_Oct'] += emission_oct
            combined[year][facility]['Emission_Nov'] += emission_nov
            combined[year][facility]['Emission_Dec'] += emission_dec
            combined[year][facility]['Emission_Jan'] += emission_jan
            combined[year][facility]['Emission_Feb'] += emission_feb
            combined[year][facility]['Emission_Mar'] += emission_mar
        else:
            combined[year][facility] = {'Emission_Apr': emission_apr,'Emission_May': emission_may,
                                        'Emission_Jun': emission_jun,'Emission_Jul': emission_jul,
                                        'Emission_Aug': emission_aug,'Emission_Sep': emission_sep,
                                        'Emission_Oct': emission_oct,'Emission_Nov': emission_nov,
                                        'Emission_Dec': emission_dec,'Emission_Jan': emission_jan,
                                        'Emission_Feb': emission_feb,'Emission_Mar': emission_mar}

    # Process second list
    for item in fuel_onsite_vehicles_list:
        year = item["Financial_Year"]
        facility = item["Facility"]
        emission_apr = item["Emission_Apr"]
        emission_may = item["Emission_May"]
        emission_jun = item["Emission_Jun"]
        emission_jul = item["Emission_Jul"]
        emission_aug = item["Emission_Aug"]
        emission_sep = item["Emission_Sep"]
        emission_oct = item["Emission_Oct"]
        emission_nov = item["Emission_Nov"]
        emission_dec = item["Emission_Dec"]
        emission_jan = item["Emission_Jan"]
        emission_feb = item["Emission_Feb"]
        emission_mar = item["Emission_Mar"]
        if year not in combined:
            combined[year] = {}
        if facility in combined[year]:
            combined[year][facility]['Emission_Apr'] += emission_apr
            combined[year][facility]['Emission_May'] += emission_may
            combined[year][facility]['Emission_Jun'] += emission_jun
            combined[year][facility]['Emission_Jul'] += emission_jul
            combined[year][facility]['Emission_Aug'] += emission_aug
            combined[year][facility]['Emission_Sep'] += emission_sep
            combined[year][facility]['Emission_Oct'] += emission_oct
            combined[year][facility]['Emission_Nov'] += emission_nov
            combined[year][facility]['Emission_Dec'] += emission_dec
            combined[year][facility]['Emission_Jan'] += emission_jan
            combined[year][facility]['Emission_Feb'] += emission_feb
            combined[year][facility]['Emission_Mar'] += emission_mar
        else:
            combined[year][facility] = {'Emission_Apr': emission_apr,'Emission_May': emission_may,
                                        'Emission_Jun': emission_jun,'Emission_Jul': emission_jul,
                                        'Emission_Aug': emission_aug,'Emission_Sep': emission_sep,
                                        'Emission_Oct': emission_oct,'Emission_Nov': emission_nov,
                                        'Emission_Dec': emission_dec,'Emission_Jan': emission_jan,
                                        'Emission_Feb': emission_feb,'Emission_Mar': emission_mar}

    # Convert the combined dictionary back to a list of dictionaries
    result = []
    for year, facilities in combined.items():
        for facility, emissions in facilities.items():
            result.append({
                "Financial_Year": year,
                "Facility": facility,
                "Emission_Apr": round(emissions['Emission_Apr'], 2),
                "Emission_May": round(emissions['Emission_May'], 2),
                "Emission_Jun": round(emissions['Emission_Jun'], 2),
                "Emission_Jul": round(emissions['Emission_Jul'], 2),
                "Emission_Aug": round(emissions['Emission_Aug'], 2),
                "Emission_Sep": round(emissions['Emission_Sep'], 2),
                "Emission_Oct": round(emissions['Emission_Oct'], 2),
                "Emission_Nov": round(emissions['Emission_Nov'], 2),
                "Emission_Dec": round(emissions['Emission_Dec'], 2),
                "Emission_Jan": round(emissions['Emission_Jan'], 2),
                "Emission_Feb": round(emissions['Emission_Feb'], 2),
                "Emission_Mar": round(emissions['Emission_Mar'], 2),
                "Total_Emission": round(round(emissions['Emission_Apr'], 2) + round(emissions['Emission_May'], 2) + round(emissions['Emission_Jun'], 2) + round(emissions['Emission_Jul'], 2) + round(emissions['Emission_Aug'], 2) + round(emissions['Emission_Sep'], 2) + round(emissions['Emission_Oct'], 2) + round(emissions['Emission_Nov'], 2) + round(emissions['Emission_Dec'], 2) + round(emissions['Emission_Jan'], 2) + round(emissions['Emission_Feb'], 2) + round(emissions['Emission_Mar'], 2), 2)
            })

    return result


def calculate_scope_1_emissions_fuel_onsite_combustion_2():
    from .models import Fuel_Consumption_Onsite_Combustion_General, EmissionFactors
    
    # Get distinct financial years and fuel types
    financial_years = Fuel_Consumption_Onsite_Combustion_General.objects.values_list('Financial_Year', flat=True).distinct()
    fuel_types = Fuel_Consumption_Onsite_Combustion_General.objects.values_list('Fuel_Type', flat=True).distinct()
    
    result = []
    
    for year in financial_years:
        for ft in fuel_types:
            record_json = {}
            records = Fuel_Consumption_Onsite_Combustion_General.objects.filter(Financial_Year=year, Fuel_Type=ft).values_list('Financial_Year', 'Fuel_Type', 'Unit')
            
            # Use a set to prevent duplicate unit processing
            units = set(record[2] for record in records)
            
            if records:
                record_json['Financial_Year'] = year
                record_json['Fuel_Type'] = ft
                
                emission_apr = 0.0
                emission_may = 0.0
                emission_jun = 0.0
                emission_jul = 0.0
                emission_aug = 0.0
                emission_sep = 0.0
                emission_oct = 0.0
                emission_nov = 0.0
                emission_dec = 0.0
                emission_jan = 0.0
                emission_feb = 0.0
                emission_mar = 0.0
                
                for unit in units:
                    all_ef = EmissionFactors.objects.get(Type_of_Emission='Fuel', Fuel=ft, Unit=unit)
                    if all_ef:
                        ef = Decimal128(str(all_ef.CO2E_Emission_Factor))
                    
                    all_records = Fuel_Consumption_Onsite_Combustion_General.objects.filter(Financial_Year=year, Fuel_Type=ft, Unit=unit)
                    
                    for apr in all_records:
                        fuel_consumption_apr = Decimal128(str(apr.Fuel_Consumption_Apr))
                        fuel_consumption_may = Decimal128(str(apr.Fuel_Consumption_May))
                        fuel_consumption_jun = Decimal128(str(apr.Fuel_Consumption_Jun))
                        fuel_consumption_jul = Decimal128(str(apr.Fuel_Consumption_Jul))
                        fuel_consumption_aug = Decimal128(str(apr.Fuel_Consumption_Aug))
                        fuel_consumption_sep = Decimal128(str(apr.Fuel_Consumption_Sep))
                        fuel_consumption_oct = Decimal128(str(apr.Fuel_Consumption_Oct))
                        fuel_consumption_nov = Decimal128(str(apr.Fuel_Consumption_Nov))
                        fuel_consumption_dec = Decimal128(str(apr.Fuel_Consumption_Dec))
                        fuel_consumption_jan = Decimal128(str(apr.Fuel_Consumption_Jan))
                        fuel_consumption_feb = Decimal128(str(apr.Fuel_Consumption_Feb))
                        fuel_consumption_mar = Decimal128(str(apr.Fuel_Consumption_Mar))
                        
                        # Calculate emissions
                        emission_apr += float(ef.to_decimal()) * float(fuel_consumption_apr.to_decimal())
                        emission_may += float(ef.to_decimal()) * float(fuel_consumption_may.to_decimal())
                        emission_jun += float(ef.to_decimal()) * float(fuel_consumption_jun.to_decimal())
                        emission_jul += float(ef.to_decimal()) * float(fuel_consumption_jul.to_decimal())
                        emission_aug += float(ef.to_decimal()) * float(fuel_consumption_aug.to_decimal())
                        emission_sep += float(ef.to_decimal()) * float(fuel_consumption_sep.to_decimal())
                        emission_oct += float(ef.to_decimal()) * float(fuel_consumption_oct.to_decimal())
                        emission_nov += float(ef.to_decimal()) * float(fuel_consumption_nov.to_decimal())
                        emission_dec += float(ef.to_decimal()) * float(fuel_consumption_dec.to_decimal())
                        emission_jan += float(ef.to_decimal()) * float(fuel_consumption_jan.to_decimal())
                        emission_feb += float(ef.to_decimal()) * float(fuel_consumption_feb.to_decimal())
                        emission_mar += float(ef.to_decimal()) * float(fuel_consumption_mar.to_decimal())
                
                record_json["Emission_Apr"] = round(emission_apr, 2)
                record_json["Emission_May"] = round(emission_may, 2)
                record_json["Emission_Jun"] = round(emission_jun, 2)
                record_json["Emission_Jul"] = round(emission_jul, 2)
                record_json["Emission_Aug"] = round(emission_aug, 2)
                record_json["Emission_Sep"] = round(emission_sep, 2)
                record_json["Emission_Oct"] = round(emission_oct, 2)
                record_json["Emission_Nov"] = round(emission_nov, 2)
                record_json["Emission_Dec"] = round(emission_dec, 2)
                record_json["Emission_Jan"] = round(emission_jan, 2)
                record_json["Emission_Feb"] = round(emission_feb, 2)
                record_json["Emission_Mar"] = round(emission_mar, 2)
                
                result.append(record_json)
    
    return result




def calculate_scope_1_emissions_fuel_onsite_vehicles_2():
    # Get a distinct list of Financial_Year
    from .models import Fuel_Consumption_Onsite_Vehicles_General, EmissionFactors
    financial_years = Fuel_Consumption_Onsite_Vehicles_General.objects.values_list('Financial_Year', flat=True).distinct()
    financial_years_list = list(financial_years)

    # Get a distinct list of Facilities
    fuel_types = Fuel_Consumption_Onsite_Vehicles_General.objects.values_list('Fuel_Type', flat=True).distinct()
    fuel_types_list = list(fuel_types)

    result = []

    for year in financial_years_list:
        for ft in fuel_types_list:
            record_json = {}
            #breakpoint()
            records = Fuel_Consumption_Onsite_Vehicles_General.objects.filter(Q(Financial_Year=year) & Q(Fuel_Type=ft) & (Q(Ownership="3rd party owned and company controlled") | Q(Ownership='Company owned and controlled'))).values_list('Financial_Year','Fuel_Type', 'Unit')
            records_list = list(records)

            if records_list:
                record_json['Financial_Year'] = year
                record_json['Fuel_Type'] = ft
                units = set([record[2] for record in records_list])

                emission_apr = 0.0
                emission_may = 0.0
                emission_jun = 0.0
                emission_jul = 0.0
                emission_aug = 0.0
                emission_sep = 0.0
                emission_oct = 0.0
                emission_nov = 0.0
                emission_dec = 0.0
                emission_jan = 0.0
                emission_feb = 0.0
                emission_mar = 0.0
                for unit in units:
                    all_ef = EmissionFactors.objects.get(Type_of_Emission='Fuel', Fuel=ft, Unit=unit)
                    if all_ef:
                        ef = all_ef.CO2E_Emission_Factor

                        all_records = Fuel_Consumption_Onsite_Vehicles_General.objects.filter(Financial_Year=year,Fuel_Type=ft,Unit=unit)

                        for apr in all_records:

                            fuel_consumption_apr = apr.Fuel_Consumption_Apr
                            fuel_consumption_may = apr.Fuel_Consumption_May
                            fuel_consumption_jun = apr.Fuel_Consumption_Jun
                            fuel_consumption_jul = apr.Fuel_Consumption_Jul
                            fuel_consumption_aug = apr.Fuel_Consumption_Aug
                            fuel_consumption_sep = apr.Fuel_Consumption_Sep
                            fuel_consumption_oct = apr.Fuel_Consumption_Oct
                            fuel_consumption_nov = apr.Fuel_Consumption_Nov
                            fuel_consumption_dec = apr.Fuel_Consumption_Dec
                            fuel_consumption_jan = apr.Fuel_Consumption_Jan
                            fuel_consumption_feb = apr.Fuel_Consumption_Feb
                            fuel_consumption_mar = apr.Fuel_Consumption_Mar

                            # Convert to Decimal128 for MongoDB
                            ef = Decimal128(str(ef))
                            fuel_consumption_apr = Decimal128(str(fuel_consumption_apr))
                            fuel_consumption_may = Decimal128(str(fuel_consumption_may))
                            fuel_consumption_jun = Decimal128(str(fuel_consumption_jun))
                            fuel_consumption_jul = Decimal128(str(fuel_consumption_jul))
                            fuel_consumption_aug = Decimal128(str(fuel_consumption_aug))
                            fuel_consumption_sep = Decimal128(str(fuel_consumption_sep))
                            fuel_consumption_oct = Decimal128(str(fuel_consumption_oct))
                            fuel_consumption_nov = Decimal128(str(fuel_consumption_nov))
                            fuel_consumption_dec = Decimal128(str(fuel_consumption_dec))
                            fuel_consumption_jan = Decimal128(str(fuel_consumption_jan))
                            fuel_consumption_feb = Decimal128(str(fuel_consumption_feb))
                            fuel_consumption_mar = Decimal128(str(fuel_consumption_mar))

                            # Calculate emissions
                            emission_apr += float(ef.to_decimal()) * float(fuel_consumption_apr.to_decimal())
                            emission_may += float(ef.to_decimal()) * float(fuel_consumption_may.to_decimal())
                            emission_jun += float(ef.to_decimal()) * float(fuel_consumption_jun.to_decimal())
                            emission_jul += float(ef.to_decimal()) * float(fuel_consumption_jul.to_decimal())
                            emission_aug += float(ef.to_decimal()) * float(fuel_consumption_aug.to_decimal())
                            emission_sep += float(ef.to_decimal()) * float(fuel_consumption_sep.to_decimal())
                            emission_oct += float(ef.to_decimal()) * float(fuel_consumption_oct.to_decimal())
                            emission_nov += float(ef.to_decimal()) * float(fuel_consumption_nov.to_decimal())
                            emission_dec += float(ef.to_decimal()) * float(fuel_consumption_dec.to_decimal())
                            emission_jan += float(ef.to_decimal()) * float(fuel_consumption_jan.to_decimal())
                            emission_feb += float(ef.to_decimal()) * float(fuel_consumption_feb.to_decimal())
                            emission_mar += float(ef.to_decimal()) * float(fuel_consumption_mar.to_decimal())

                record_json["Emission_Apr"] = round(emission_apr, 2)
                record_json["Emission_May"] = round(emission_may, 2)
                record_json["Emission_Jun"] = round(emission_jun, 2)
                record_json["Emission_Jul"] = round(emission_jul, 2)
                record_json["Emission_Aug"] = round(emission_aug, 2)
                record_json["Emission_Sep"] = round(emission_sep, 2)
                record_json["Emission_Oct"] = round(emission_oct, 2)
                record_json["Emission_Nov"] = round(emission_nov, 2)
                record_json["Emission_Dec"] = round(emission_dec, 2)
                record_json["Emission_Jan"] = round(emission_jan, 2)
                record_json["Emission_Feb"] = round(emission_feb, 2)
                record_json["Emission_Mar"] = round(emission_mar, 2)
                result.append(record_json)
    return result



def calculate_scope_1_emissions_by_fuel():
    fuel_onsite_combustion_list = calculate_scope_1_emissions_fuel_onsite_combustion_2()
    fuel_onsite_vehicles_list = calculate_scope_1_emissions_fuel_onsite_vehicles_2()

    combined = {}

    # Process first list
    for item in fuel_onsite_combustion_list:
        year = item["Financial_Year"]
        fuel_type = item["Fuel_Type"]
        emission_apr = item["Emission_Apr"]
        emission_may = item["Emission_May"]
        emission_jun = item["Emission_Jun"]
        emission_jul = item["Emission_Jul"]
        emission_aug = item["Emission_Aug"]
        emission_sep = item["Emission_Sep"]
        emission_oct = item["Emission_Oct"]
        emission_nov = item["Emission_Nov"]
        emission_dec = item["Emission_Dec"]
        emission_jan = item["Emission_Jan"]
        emission_feb = item["Emission_Feb"]
        emission_mar = item["Emission_Mar"]

        if year not in combined:
            combined[year] = {}
        if fuel_type in combined[year]:
            combined[year][fuel_type]['Emission_Apr'] += emission_apr
            combined[year][fuel_type]['Emission_May'] += emission_may
            combined[year][fuel_type]['Emission_Jun'] += emission_jun
            combined[year][fuel_type]['Emission_Jul'] += emission_jul
            combined[year][fuel_type]['Emission_Aug'] += emission_aug
            combined[year][fuel_type]['Emission_Sep'] += emission_sep
            combined[year][fuel_type]['Emission_Oct'] += emission_oct
            combined[year][fuel_type]['Emission_Nov'] += emission_nov
            combined[year][fuel_type]['Emission_Dec'] += emission_dec
            combined[year][fuel_type]['Emission_Jan'] += emission_jan
            combined[year][fuel_type]['Emission_Feb'] += emission_feb
            combined[year][fuel_type]['Emission_Mar'] += emission_mar
        else:
            combined[year][fuel_type] = {'Emission_Apr': emission_apr,'Emission_May': emission_may,
                                        'Emission_Jun': emission_jun,'Emission_Jul': emission_jul,
                                        'Emission_Aug': emission_aug,'Emission_Sep': emission_sep,
                                        'Emission_Oct': emission_oct,'Emission_Nov': emission_nov,
                                        'Emission_Dec': emission_dec,'Emission_Jan': emission_jan,
                                        'Emission_Feb': emission_feb,'Emission_Mar': emission_mar}

    # Process second list
    for item in fuel_onsite_vehicles_list:
        year = item["Financial_Year"]
        fuel_type = item["Fuel_Type"]
        emission_apr = item["Emission_Apr"]
        emission_may = item["Emission_May"]
        emission_jun = item["Emission_Jun"]
        emission_jul = item["Emission_Jul"]
        emission_aug = item["Emission_Aug"]
        emission_sep = item["Emission_Sep"]
        emission_oct = item["Emission_Oct"]
        emission_nov = item["Emission_Nov"]
        emission_dec = item["Emission_Dec"]
        emission_jan = item["Emission_Jan"]
        emission_feb = item["Emission_Feb"]
        emission_mar = item["Emission_Mar"]
        if year not in combined:
            combined[year] = {}
        if fuel_type in combined[year]:
            combined[year][fuel_type]['Emission_Apr'] += emission_apr
            combined[year][fuel_type]['Emission_May'] += emission_may
            combined[year][fuel_type]['Emission_Jun'] += emission_jun
            combined[year][fuel_type]['Emission_Jul'] += emission_jul
            combined[year][fuel_type]['Emission_Aug'] += emission_aug
            combined[year][fuel_type]['Emission_Sep'] += emission_sep
            combined[year][fuel_type]['Emission_Oct'] += emission_oct
            combined[year][fuel_type]['Emission_Nov'] += emission_nov
            combined[year][fuel_type]['Emission_Dec'] += emission_dec
            combined[year][fuel_type]['Emission_Jan'] += emission_jan
            combined[year][fuel_type]['Emission_Feb'] += emission_feb
            combined[year][fuel_type]['Emission_Mar'] += emission_mar
        else:
            combined[year][fuel_type] = {'Emission_Apr': emission_apr,'Emission_May': emission_may,
                                        'Emission_Jun': emission_jun,'Emission_Jul': emission_jul,
                                        'Emission_Aug': emission_aug,'Emission_Sep': emission_sep,
                                        'Emission_Oct': emission_oct,'Emission_Nov': emission_nov,
                                        'Emission_Dec': emission_dec,'Emission_Jan': emission_jan,
                                        'Emission_Feb': emission_feb,'Emission_Mar': emission_mar}

    # Convert the combined dictionary back to a list of dictionaries
    result = []
    for year, fuel_types in combined.items():
        for fuel_type, emissions in fuel_types.items():
            result.append({
                "Financial_Year": year,
                "Fuel_Type": fuel_type,
                "Emission_Apr": round(emissions['Emission_Apr'], 2),
                "Emission_May": round(emissions['Emission_May'], 2),
                "Emission_Jun": round(emissions['Emission_Jun'], 2),
                "Emission_Jul": round(emissions['Emission_Jul'], 2),
                "Emission_Aug": round(emissions['Emission_Aug'], 2),
                "Emission_Sep": round(emissions['Emission_Sep'], 2),
                "Emission_Oct": round(emissions['Emission_Oct'], 2),
                "Emission_Nov": round(emissions['Emission_Nov'], 2),
                "Emission_Dec": round(emissions['Emission_Dec'], 2),
                "Emission_Jan": round(emissions['Emission_Jan'], 2),
                "Emission_Feb": round(emissions['Emission_Feb'], 2),
                "Emission_Mar": round(emissions['Emission_Mar'], 2),
                "Total_Emission": round(round(emissions['Emission_Apr'], 2) + round(emissions['Emission_May'], 2) + round(emissions['Emission_Jun'], 2) + round(emissions['Emission_Jul'], 2) + round(emissions['Emission_Aug'], 2) + round(emissions['Emission_Sep'], 2) + round(emissions['Emission_Oct'], 2) + round(emissions['Emission_Nov'], 2) + round(emissions['Emission_Dec'], 2) + round(emissions['Emission_Jan'], 2) + round(emissions['Emission_Feb'], 2) + round(emissions['Emission_Mar'], 2), 2)
            })

    return result



def calculate_scope_1_emissions_fuel_onsite_combustion_3():
    ghg_type_list1 = ["CO2E", "CO2", "CH4", "N2O"]
    from .models import Fuel_Consumption_Onsite_Combustion_General, EmissionFactors
    # Get a distinct list of Financial_Year
    financial_years = Fuel_Consumption_Onsite_Combustion_General.objects.values_list('Financial_Year', flat=True).distinct()
    financial_years_list = list(financial_years)

    result = []
    for l in ghg_type_list1:
        for year in financial_years_list:
            #breakpoint()
            record_json = {}
            record_json["GHG_Type"] = l
            record_json["Financial_Year"] = year

            records = Fuel_Consumption_Onsite_Combustion_General.objects.filter(Financial_Year=year)
            records_list = list(records)

            emission_apr = Decimal('0.0')
            emission_may = Decimal('0.0')
            emission_jun = Decimal('0.0')
            emission_jul = Decimal('0.0')
            emission_aug = Decimal('0.0')
            emission_sep = Decimal('0.0')
            emission_oct = Decimal('0.0')
            emission_nov = Decimal('0.0')
            emission_dec = Decimal('0.0')
            emission_jan = Decimal('0.0')
            emission_feb = Decimal('0.0')
            emission_mar = Decimal('0.0')
            for rec in records_list:
                fuel_type = rec.Fuel_Type
                unit = rec.Unit
                consumption_apr = Decimal(str(rec.Fuel_Consumption_Apr))
                consumption_may = Decimal(str(rec.Fuel_Consumption_May))
                consumption_jun = Decimal(str(rec.Fuel_Consumption_Jun))
                consumption_jul = Decimal(str(rec.Fuel_Consumption_Jul))
                consumption_aug = Decimal(str(rec.Fuel_Consumption_Aug))
                consumption_sep = Decimal(str(rec.Fuel_Consumption_Sep))
                consumption_oct = Decimal(str(rec.Fuel_Consumption_Oct))
                consumption_nov = Decimal(str(rec.Fuel_Consumption_Nov))
                consumption_dec = Decimal(str(rec.Fuel_Consumption_Dec))
                consumption_jan = Decimal(str(rec.Fuel_Consumption_Jan))
                consumption_feb = Decimal(str(rec.Fuel_Consumption_Feb))
                consumption_mar = Decimal(str(rec.Fuel_Consumption_Mar))

                ef_all = EmissionFactors.objects.get(Type_of_Emission='Fuel', Fuel=fuel_type, Unit=unit)

                if l == "CO2E":
                    ef = Decimal(str(ef_all.CO2E_Emission_Factor))
                elif l == "CO2":
                    ef = Decimal(str(ef_all.CO2_Emission_Factor))
                elif l == "CH4":
                    ef = Decimal(str(ef_all.CH4_Emission_Factor))
                elif l == "N2O":
                    ef = Decimal(str(ef_all.N2O_Emission_Factor))

                emission_apr += ef * consumption_apr
                emission_may += ef * consumption_may
                emission_jun += ef * consumption_jun
                emission_jul += ef * consumption_jul
                emission_aug += ef * consumption_aug
                emission_sep += ef * consumption_sep
                emission_oct += ef * consumption_oct
                emission_nov += ef * consumption_nov
                emission_dec += ef * consumption_dec
                emission_jan += ef * consumption_jan
                emission_feb += ef * consumption_feb
                emission_mar += ef * consumption_mar

            record_json["Emission_Apr"] = round(float(emission_apr), 2)
            record_json["Emission_May"] = round(float(emission_may), 2)
            record_json["Emission_Jun"] = round(float(emission_jun), 2)
            record_json["Emission_Jul"] = round(float(emission_jul), 2)
            record_json["Emission_Aug"] = round(float(emission_aug), 2)
            record_json["Emission_Sep"] = round(float(emission_sep), 2)
            record_json["Emission_Oct"] = round(float(emission_oct), 2)
            record_json["Emission_Nov"] = round(float(emission_nov), 2)
            record_json["Emission_Dec"] = round(float(emission_dec), 2)
            record_json["Emission_Jan"] = round(float(emission_jan), 2)
            record_json["Emission_Feb"] = round(float(emission_feb), 2)
            record_json["Emission_Mar"] = round(float(emission_mar), 2)
            result.append(record_json)

    return result



def calculate_scope_1_emissions_fuel_onsite_vehicles_3():
    ghg_type_list1 = ["CO2E", "CO2", "CH4", "N2O"]
    from .models import Fuel_Consumption_Onsite_Vehicles_General, EmissionFactors
    # Get a distinct list of Financial_Year
    financial_years = Fuel_Consumption_Onsite_Vehicles_General.objects.values_list('Financial_Year', flat=True).distinct()
    financial_years_list = list(financial_years)

    result = []
    for l in ghg_type_list1:
        for year in financial_years_list:
            #breakpoint()
            record_json = {}
            record_json["GHG_Type"] = l
            record_json["Financial_Year"] = year

            records = Fuel_Consumption_Onsite_Vehicles_General.objects.filter(Q(Financial_Year=year) & (Q(Ownership="3rd party owned and company controlled") | Q(Ownership='Company owned and controlled')))
            records_list = list(records)

            emission_apr = Decimal('0.0')
            emission_may = Decimal('0.0')
            emission_jun = Decimal('0.0')
            emission_jul = Decimal('0.0')
            emission_aug = Decimal('0.0')
            emission_sep = Decimal('0.0')
            emission_oct = Decimal('0.0')
            emission_nov = Decimal('0.0')
            emission_dec = Decimal('0.0')
            emission_jan = Decimal('0.0')
            emission_feb = Decimal('0.0')
            emission_mar = Decimal('0.0')
            for rec in records_list:
                fuel_type = rec.Fuel_Type
                unit = rec.Unit
                consumption_apr = Decimal(str(rec.Fuel_Consumption_Apr))
                consumption_may = Decimal(str(rec.Fuel_Consumption_May))
                consumption_jun = Decimal(str(rec.Fuel_Consumption_Jun))
                consumption_jul = Decimal(str(rec.Fuel_Consumption_Jul))
                consumption_aug = Decimal(str(rec.Fuel_Consumption_Aug))
                consumption_sep = Decimal(str(rec.Fuel_Consumption_Sep))
                consumption_oct = Decimal(str(rec.Fuel_Consumption_Oct))
                consumption_nov = Decimal(str(rec.Fuel_Consumption_Nov))
                consumption_dec = Decimal(str(rec.Fuel_Consumption_Dec))
                consumption_jan = Decimal(str(rec.Fuel_Consumption_Jan))
                consumption_feb = Decimal(str(rec.Fuel_Consumption_Feb))
                consumption_mar = Decimal(str(rec.Fuel_Consumption_Mar))

                ef_all = EmissionFactors.objects.get(Type_of_Emission='Fuel', Fuel=fuel_type, Unit=unit)

                if l == "CO2E":
                    ef = Decimal(str(ef_all.CO2E_Emission_Factor))
                elif l == "CO2":
                    ef = Decimal(str(ef_all.CO2_Emission_Factor))
                elif l == "CH4":
                    ef = Decimal(str(ef_all.CH4_Emission_Factor))
                elif l == "N2O":
                    ef = Decimal(str(ef_all.N2O_Emission_Factor))

                emission_apr += ef * consumption_apr
                emission_may += ef * consumption_may
                emission_jun += ef * consumption_jun
                emission_jul += ef * consumption_jul
                emission_aug += ef * consumption_aug
                emission_sep += ef * consumption_sep
                emission_oct += ef * consumption_oct
                emission_nov += ef * consumption_nov
                emission_dec += ef * consumption_dec
                emission_jan += ef * consumption_jan
                emission_feb += ef * consumption_feb
                emission_mar += ef * consumption_mar

            record_json["Emission_Apr"] = round(float(emission_apr), 2)
            record_json["Emission_May"] = round(float(emission_may), 2)
            record_json["Emission_Jun"] = round(float(emission_jun), 2)
            record_json["Emission_Jul"] = round(float(emission_jul), 2)
            record_json["Emission_Aug"] = round(float(emission_aug), 2)
            record_json["Emission_Sep"] = round(float(emission_sep), 2)
            record_json["Emission_Oct"] = round(float(emission_oct), 2)
            record_json["Emission_Nov"] = round(float(emission_nov), 2)
            record_json["Emission_Dec"] = round(float(emission_dec), 2)
            record_json["Emission_Jan"] = round(float(emission_jan), 2)
            record_json["Emission_Feb"] = round(float(emission_feb), 2)
            record_json["Emission_Mar"] = round(float(emission_mar), 2)
            result.append(record_json)
    return result



def calculate_scope_1_emissions_by_ghg_type():
    fuel_onsite_combustion_list = calculate_scope_1_emissions_fuel_onsite_combustion_3()
    fuel_onsite_vehicles_list = calculate_scope_1_emissions_fuel_onsite_vehicles_3()

    combined = {}

    # Process first list
    for item in fuel_onsite_combustion_list:

        year = item["Financial_Year"]
        ghg_type = item["GHG_Type"]
        emission_apr = item["Emission_Apr"]
        emission_may = item["Emission_May"]
        emission_jun = item["Emission_Jun"]
        emission_jul = item["Emission_Jul"]
        emission_aug = item["Emission_Aug"]
        emission_sep = item["Emission_Sep"]
        emission_oct = item["Emission_Oct"]
        emission_nov = item["Emission_Nov"]
        emission_dec = item["Emission_Dec"]
        emission_jan = item["Emission_Jan"]
        emission_feb = item["Emission_Feb"]
        emission_mar = item["Emission_Mar"]

        if year not in combined:
            combined[year] = {}
        if ghg_type in combined[year]:
            combined[year][ghg_type]['Emission_Apr'] += emission_apr
            combined[year][ghg_type]['Emission_May'] += emission_may
            combined[year][ghg_type]['Emission_Jun'] += emission_jun
            combined[year][ghg_type]['Emission_Jul'] += emission_jul
            combined[year][ghg_type]['Emission_Aug'] += emission_aug
            combined[year][ghg_type]['Emission_Sep'] += emission_sep
            combined[year][ghg_type]['Emission_Oct'] += emission_oct
            combined[year][ghg_type]['Emission_Nov'] += emission_nov
            combined[year][ghg_type]['Emission_Dec'] += emission_dec
            combined[year][ghg_type]['Emission_Jan'] += emission_jan
            combined[year][ghg_type]['Emission_Feb'] += emission_feb
            combined[year][ghg_type]['Emission_Mar'] += emission_mar
        else:
            combined[year][ghg_type] = {'Emission_Apr': emission_apr,'Emission_May': emission_may,
                                        'Emission_Jun': emission_jun,'Emission_Jul': emission_jul,
                                        'Emission_Aug': emission_aug,'Emission_Sep': emission_sep,
                                        'Emission_Oct': emission_oct,'Emission_Nov': emission_nov,
                                        'Emission_Dec': emission_dec,'Emission_Jan': emission_jan,
                                        'Emission_Feb': emission_feb,'Emission_Mar': emission_mar}

    # Process second list
    for item in fuel_onsite_vehicles_list:
        year = item["Financial_Year"]
        ghg_type = item["GHG_Type"]
        emission_apr = item["Emission_Apr"]
        emission_may = item["Emission_May"]
        emission_jun = item["Emission_Jun"]
        emission_jul = item["Emission_Jul"]
        emission_aug = item["Emission_Aug"]
        emission_sep = item["Emission_Sep"]
        emission_oct = item["Emission_Oct"]
        emission_nov = item["Emission_Nov"]
        emission_dec = item["Emission_Dec"]
        emission_jan = item["Emission_Jan"]
        emission_feb = item["Emission_Feb"]
        emission_mar = item["Emission_Mar"]
        if year not in combined:
            combined[year] = {}
        if ghg_type in combined[year]:
            combined[year][ghg_type]['Emission_Apr'] += emission_apr
            combined[year][ghg_type]['Emission_May'] += emission_may
            combined[year][ghg_type]['Emission_Jun'] += emission_jun
            combined[year][ghg_type]['Emission_Jul'] += emission_jul
            combined[year][ghg_type]['Emission_Aug'] += emission_aug
            combined[year][ghg_type]['Emission_Sep'] += emission_sep
            combined[year][ghg_type]['Emission_Oct'] += emission_oct
            combined[year][ghg_type]['Emission_Nov'] += emission_nov
            combined[year][ghg_type]['Emission_Dec'] += emission_dec
            combined[year][ghg_type]['Emission_Jan'] += emission_jan
            combined[year][ghg_type]['Emission_Feb'] += emission_feb
            combined[year][ghg_type]['Emission_Mar'] += emission_mar
        else:
            combined[year][ghg_type] = {'Emission_Apr': emission_apr,'Emission_May': emission_may,
                                        'Emission_Jun': emission_jun,'Emission_Jul': emission_jul,
                                        'Emission_Aug': emission_aug,'Emission_Sep': emission_sep,
                                        'Emission_Oct': emission_oct,'Emission_Nov': emission_nov,
                                        'Emission_Dec': emission_dec,'Emission_Jan': emission_jan,
                                        'Emission_Feb': emission_feb,'Emission_Mar': emission_mar}

    # Convert the combined dictionary back to a list of dictionaries
    result = []
    for year, ghg_types in combined.items():
        for ghg_type, emissions in ghg_types.items():
            result.append({
                "Financial_Year": year,
                "GHG_Type": ghg_type,
                "Emission_Apr": round(emissions['Emission_Apr'], 2),
                "Emission_May": round(emissions['Emission_May'], 2),
                "Emission_Jun": round(emissions['Emission_Jun'], 2),
                "Emission_Jul": round(emissions['Emission_Jul'], 2),
                "Emission_Aug": round(emissions['Emission_Aug'], 2),
                "Emission_Sep": round(emissions['Emission_Sep'], 2),
                "Emission_Oct": round(emissions['Emission_Oct'], 2),
                "Emission_Nov": round(emissions['Emission_Nov'], 2),
                "Emission_Dec": round(emissions['Emission_Dec'], 2),
                "Emission_Jan": round(emissions['Emission_Jan'], 2),
                "Emission_Feb": round(emissions['Emission_Feb'], 2),
                "Emission_Mar": round(emissions['Emission_Mar'], 2),
                "Total_Emission": round(round(emissions['Emission_Apr'], 2) + round(emissions['Emission_May'], 2) + round(emissions['Emission_Jun'], 2) + round(emissions['Emission_Jul'], 2) + round(emissions['Emission_Aug'], 2) + round(emissions['Emission_Sep'], 2) + round(emissions['Emission_Oct'], 2) + round(emissions['Emission_Nov'], 2) + round(emissions['Emission_Dec'], 2) + round(emissions['Emission_Jan'], 2) + round(emissions['Emission_Feb'], 2) + round(emissions['Emission_Mar'], 2), 2)
            })

    return result

            

def calculate_scope_1_intensity():

    result = []
    from .models import Scope1_Emissions_by_Facilities
    from CompanyDetails.models import Turnover
    all_objects = Scope1_Emissions_by_Facilities.objects.all()
    for obj in all_objects:
        record_json = {}
        record_json["Financial_Year"] = obj.Financial_Year
        record_json["Facility"] = obj.Facility
        try:
            turnover = Turnover.objects.get(Financial_Year=record_json["Financial_Year"])
            turnover_apr = Decimal(turnover.Turnover_Apr.to_decimal())
            turnover_may = Decimal(turnover.Turnover_May.to_decimal())
            turnover_jun = Decimal(turnover.Turnover_Jun.to_decimal())
            turnover_jul = Decimal(turnover.Turnover_Jul.to_decimal())
            turnover_aug = Decimal(turnover.Turnover_Aug.to_decimal())
            turnover_sep = Decimal(turnover.Turnover_Sep.to_decimal())
            turnover_oct = Decimal(turnover.Turnover_Oct.to_decimal())
            turnover_nov = Decimal(turnover.Turnover_Nov.to_decimal())
            turnover_dec = Decimal(turnover.Turnover_Dec.to_decimal())
            turnover_jan = Decimal(turnover.Turnover_Jan.to_decimal())
            turnover_feb = Decimal(turnover.Turnover_Feb.to_decimal())
            turnover_mar = Decimal(turnover.Turnover_Mar.to_decimal())
            
            emission_apr = Decimal(obj.Emission_Apr.to_decimal())
            emission_may = Decimal(obj.Emission_May.to_decimal())
            emission_jun = Decimal(obj.Emission_Jun.to_decimal())
            emission_jul = Decimal(obj.Emission_Jul.to_decimal())
            emission_aug = Decimal(obj.Emission_Aug.to_decimal())
            emission_sep = Decimal(obj.Emission_Sep.to_decimal())
            emission_oct = Decimal(obj.Emission_Oct.to_decimal())
            emission_nov = Decimal(obj.Emission_Nov.to_decimal())
            emission_dec = Decimal(obj.Emission_Dec.to_decimal())
            emission_jan = Decimal(obj.Emission_Jan.to_decimal())
            emission_feb = Decimal(obj.Emission_Feb.to_decimal())
            emission_mar = Decimal(obj.Emission_Mar.to_decimal())

            record_json["Intensity_Apr"] = round(float(emission_apr / turnover_apr), 2) if turnover_apr > 0 else 0
            record_json["Intensity_May"] = round(float(emission_may / turnover_may), 2) if turnover_may > 0 else 0
            record_json["Intensity_Jun"] = round(float(emission_jun / turnover_jun), 2) if turnover_jun > 0 else 0
            record_json["Intensity_Jul"] = round(float(emission_jul / turnover_jul), 2) if turnover_jul > 0 else 0
            record_json["Intensity_Aug"] = round(float(emission_aug / turnover_aug), 2) if turnover_aug > 0 else 0
            record_json["Intensity_Sep"] = round(float(emission_sep / turnover_sep), 2) if turnover_sep > 0 else 0
            record_json["Intensity_Oct"] = round(float(emission_oct / turnover_oct), 2) if turnover_oct > 0 else 0
            record_json["Intensity_Nov"] = round(float(emission_nov / turnover_nov), 2) if turnover_nov > 0 else 0
            record_json["Intensity_Dec"] = round(float(emission_dec / turnover_dec), 2) if turnover_dec > 0 else 0
            record_json["Intensity_Jan"] = round(float(emission_jan / turnover_jan), 2) if turnover_jan > 0 else 0
            record_json["Intensity_Feb"] = round(float(emission_feb / turnover_feb), 2) if turnover_feb > 0 else 0
            record_json["Intensity_Mar"] = round(float(emission_mar / turnover_mar), 2) if turnover_mar > 0 else 0
            record_json["Total_Intensity"] = round(record_json["Intensity_Apr"] + record_json["Intensity_May"] + record_json["Intensity_Jun"] + record_json["Intensity_Jul"] + record_json["Intensity_Aug"] + record_json["Intensity_Sep"] + record_json["Intensity_Oct"] + record_json["Intensity_Nov"] + record_json["Intensity_Dec"] + record_json["Intensity_Jan"] + record_json["Intensity_Feb"] + record_json["Intensity_Mar"], 2)

            result.append(record_json)

        except Turnover.DoesNotExist:
            record_json["Intensity_Apr"] = 0
            record_json["Intensity_May"] = 0
            record_json["Intensity_Jun"] = 0
            record_json["Intensity_Jul"] = 0
            record_json["Intensity_Aug"] = 0
            record_json["Intensity_Sep"] = 0
            record_json["Intensity_Oct"] = 0
            record_json["Intensity_Nov"] = 0
            record_json["Intensity_Dec"] = 0
            record_json["Intensity_Jan"] = 0
            record_json["Intensity_Feb"] = 0
            record_json["Intensity_Mar"] = 0
            record_json["Total_Intensity"] = 0     
            result.append(record_json)   

    try:
        intensity_years = Scope1_Emissions_by_Facilities.objects.values_list('Financial_Year', flat=True).distinct()
        turnover_years = Turnover.objects.values_list('Financial_Year', flat=True)
        elements_in_list2_not_in_list1 = list(set(turnover_years) - set(intensity_years))
        for elem in elements_in_list2_not_in_list1:
            record_json = {}
            record_json["Financial_Year"] = elem
            record_json["Facility"] = "NA"
            record_json["Intensity_Apr"] = 0
            record_json["Intensity_May"] = 0
            record_json["Intensity_Jun"] = 0
            record_json["Intensity_Jul"] = 0
            record_json["Intensity_Aug"] = 0
            record_json["Intensity_Sep"] = 0
            record_json["Intensity_Oct"] = 0
            record_json["Intensity_Nov"] = 0
            record_json["Intensity_Dec"] = 0
            record_json["Intensity_Jan"] = 0
            record_json["Intensity_Feb"] = 0
            record_json["Intensity_Mar"] = 0
            record_json["Total_Intensity"] = 0
            result.append(record_json)
    except Exception as e:
        print(f"An error occurred: {e}")

    return result    



def calculate_scope2_emission_by_facilities():
    
    from .models import EmissionFactors, Electricity_Consumption_mwh
    ef_all = EmissionFactors.objects.filter(Type_of_Emission='Electricity').first()
    if ef_all:
        ef = ef_all.CO2_Emission_Factor

    # Perform the query
    purchased_only = Electricity_Consumption_mwh.objects.filter(Source='Grid')

    result = []
    # Print the results
    for document in purchased_only:
        record_json = {}
        record_json["Financial_Year"] = document.Financial_Year
        record_json["Facility"] = document.Facility
        emission_apr = Decimal(document.Electricity_Consumption_Apr.to_decimal())
        emission_may = Decimal(document.Electricity_Consumption_May.to_decimal())
        emission_jun = Decimal(document.Electricity_Consumption_Jun.to_decimal())
        emission_jul = Decimal(document.Electricity_Consumption_Jul.to_decimal())
        emission_aug = Decimal(document.Electricity_Consumption_Aug.to_decimal())
        emission_sep = Decimal(document.Electricity_Consumption_Sep.to_decimal())
        emission_oct = Decimal(document.Electricity_Consumption_Oct.to_decimal())
        emission_nov = Decimal(document.Electricity_Consumption_Nov.to_decimal())
        emission_dec = Decimal(document.Electricity_Consumption_Dec.to_decimal())
        emission_jan = Decimal(document.Electricity_Consumption_Jan.to_decimal())
        emission_feb = Decimal(document.Electricity_Consumption_Feb.to_decimal())
        emission_mar = Decimal(document.Electricity_Consumption_Mar.to_decimal())

        record_json["Emission_Apr"] = round(float(emission_apr) * ef, 2)
        record_json["Emission_May"] = round(float(emission_may) * ef, 2)
        record_json["Emission_Jun"] = round(float(emission_jun) * ef, 2)
        record_json["Emission_Jul"] = round(float(emission_jul) * ef, 2)
        record_json["Emission_Aug"] = round(float(emission_aug) * ef, 2)
        record_json["Emission_Sep"] = round(float(emission_sep) * ef, 2)
        record_json["Emission_Oct"] = round(float(emission_oct) * ef, 2)
        record_json["Emission_Nov"] = round(float(emission_nov) * ef, 2)
        record_json["Emission_Dec"] = round(float(emission_dec) * ef, 2)
        record_json["Emission_Jan"] = round(float(emission_jan) * ef, 2)
        record_json["Emission_Feb"] = round(float(emission_feb) * ef, 2)
        record_json["Emission_Mar"] = round(float(emission_mar) * ef, 2)
        record_json["Total_Emission"] = round(round(record_json['Emission_Apr'], 2) + round(record_json['Emission_May'], 2) + round(record_json['Emission_Jun'], 2) + round(record_json['Emission_Jul'], 2) + round(record_json['Emission_Aug'], 2) + round(record_json['Emission_Sep'], 2) + round(record_json['Emission_Oct'], 2) + round(record_json['Emission_Nov'], 2) + round(record_json['Emission_Dec'], 2) + round(record_json['Emission_Jan'], 2) + round(record_json['Emission_Feb'], 2) + round(record_json['Emission_Mar'], 2), 2)
        result.append(record_json)

    return result



def calculate_scope2_emissions_by_fuel():
    # Get a distinct list of Financial_Year
    from .models import Electricity_Consumption_mwh, EmissionFactors
    financial_years = Electricity_Consumption_mwh.objects.filter(Source='Grid').values_list('Financial_Year', flat=True).distinct()
    financial_years_list = list(financial_years)

    result = []
    for year in financial_years_list:
        purchased_only = Electricity_Consumption_mwh.objects.filter(Financial_Year=year,Source='Grid')
        record_json = {}
        record_json["Financial_Year"] = year
        record_json["Type"] = "Grid"

        ef_all = EmissionFactors.objects.filter(Type_of_Emission='Electricity').first()
        if ef_all:
            ef = ef_all.CO2_Emission_Factor

        emission_apr2 = 0
        emission_may2 = 0
        emission_jun2 = 0
        emission_jul2 = 0
        emission_aug2 = 0
        emission_sep2 = 0
        emission_oct2 = 0
        emission_nov2 = 0
        emission_dec2 = 0
        emission_jan2 = 0
        emission_feb2 = 0
        emission_mar2 = 0
        for obj in purchased_only:
            
            emission_apr = Decimal(obj.Electricity_Consumption_Apr.to_decimal())
            emission_apr1 = round(float(emission_apr) * ef, 2)
            emission_apr2 += round(emission_apr1, 2)

            emission_may = Decimal(obj.Electricity_Consumption_May.to_decimal())
            emission_may1 = round(float(emission_may) * ef, 2)
            emission_may2 += round(emission_may1, 2)

            emission_jun = Decimal(obj.Electricity_Consumption_Jun.to_decimal())
            emission_jun1 = round(float(emission_jun) * ef, 2)
            emission_jun2 += round(emission_jun1, 2)

            emission_jul = Decimal(obj.Electricity_Consumption_Jul.to_decimal())
            emission_jul1 = round(float(emission_jul) * ef, 2)
            emission_jul2 += round(emission_jul1, 2)

            emission_aug = Decimal(obj.Electricity_Consumption_Aug.to_decimal())
            emission_aug1 = round(float(emission_aug) * ef, 2)
            emission_aug2 += round(emission_aug1, 2)

            emission_sep = Decimal(obj.Electricity_Consumption_Sep.to_decimal())
            emission_sep1 = round(float(emission_sep) * ef, 2)
            emission_sep2 += round(emission_sep1, 2)

            emission_oct = Decimal(obj.Electricity_Consumption_Oct.to_decimal())
            emission_oct1 = round(float(emission_oct) * ef, 2)
            emission_oct2 += round(emission_oct1, 2)

            emission_nov = Decimal(obj.Electricity_Consumption_Nov.to_decimal())
            emission_nov1 = round(float(emission_nov) * ef, 2)
            emission_nov2 += round(emission_nov1, 2)

            emission_dec = Decimal(obj.Electricity_Consumption_Dec.to_decimal())
            emission_dec1 = round(float(emission_dec) * ef, 2)
            emission_dec2 += round(emission_dec1, 2)

            emission_jan = Decimal(obj.Electricity_Consumption_Jan.to_decimal())
            emission_jan1 = round(float(emission_jan) * ef, 2)
            emission_jan2 += round(emission_jan1, 2)

            emission_feb = Decimal(obj.Electricity_Consumption_Feb.to_decimal())
            emission_feb1 = round(float(emission_feb) * ef, 2)
            emission_feb2 += round(emission_feb1, 2)

            emission_mar = Decimal(obj.Electricity_Consumption_Mar.to_decimal())
            emission_mar1 = round(float(emission_mar) * ef, 2)
            emission_mar2 += round(emission_mar1, 2)

        record_json["Emission_Apr"] = round(emission_apr2, 2)
        record_json["Emission_May"] = round(emission_may2, 2)
        record_json["Emission_Jun"] = round(emission_jun2, 2)
        record_json["Emission_Jul"] = round(emission_jul2, 2)
        record_json["Emission_Aug"] = round(emission_aug2, 2)
        record_json["Emission_Sep"] = round(emission_sep2, 2)
        record_json["Emission_Oct"] = round(emission_oct2, 2)
        record_json["Emission_Nov"] = round(emission_nov2, 2)
        record_json["Emission_Dec"] = round(emission_dec2, 2)
        record_json["Emission_Jan"] = round(emission_jan2, 2)
        record_json["Emission_Feb"] = round(emission_feb2, 2)
        record_json["Emission_Mar"] = round(emission_mar2, 2)
        record_json["Total_Emission"] = round(round(record_json['Emission_Apr'], 2) + round(record_json['Emission_May'], 2) + round(record_json['Emission_Jun'], 2) + round(record_json['Emission_Jul'], 2) + round(record_json['Emission_Aug'], 2) + round(record_json['Emission_Sep'], 2) + round(record_json['Emission_Oct'], 2) + round(record_json['Emission_Nov'], 2) + round(record_json['Emission_Dec'], 2) + round(record_json['Emission_Jan'], 2) + round(record_json['Emission_Feb'], 2) + round(record_json['Emission_Mar'], 2), 2)
        result.append(record_json)

    return result



def calculate_scope2_emissions_by_ghg_type():
    GHG_Type = ["CO2E", "CO2"]

    # Get a distinct list of Financial_Year
    from .models import Electricity_Consumption_mwh, EmissionFactors
    financial_years = Electricity_Consumption_mwh.objects.filter(Source='Grid').values_list('Financial_Year', flat=True).distinct()
    financial_years_list = list(financial_years)

    result = []
    for type in GHG_Type:
        for year in financial_years_list:
            record_json = {}
            record_json["GHG_Type"] = type
            record_json["Financial_Year"] = year

            records = Electricity_Consumption_mwh.objects.filter(Financial_Year=year)
            records_list = list(records)

            emission_apr = Decimal('0.0')
            emission_may = Decimal('0.0')
            emission_jun = Decimal('0.0')
            emission_jul = Decimal('0.0')
            emission_aug = Decimal('0.0')
            emission_sep = Decimal('0.0')
            emission_oct = Decimal('0.0')
            emission_nov = Decimal('0.0')
            emission_dec = Decimal('0.0')
            emission_jan = Decimal('0.0')
            emission_feb = Decimal('0.0')
            emission_mar = Decimal('0.0')
            
            for rec in records_list:
                consumption_apr = Decimal(str(rec.Electricity_Consumption_Apr))
                consumption_may = Decimal(str(rec.Electricity_Consumption_May))
                consumption_jun = Decimal(str(rec.Electricity_Consumption_Jun))
                consumption_jul = Decimal(str(rec.Electricity_Consumption_Jul))
                consumption_aug = Decimal(str(rec.Electricity_Consumption_Aug))
                consumption_sep = Decimal(str(rec.Electricity_Consumption_Sep))
                consumption_oct = Decimal(str(rec.Electricity_Consumption_Oct))
                consumption_nov = Decimal(str(rec.Electricity_Consumption_Nov))
                consumption_dec = Decimal(str(rec.Electricity_Consumption_Dec))
                consumption_jan = Decimal(str(rec.Electricity_Consumption_Jan))
                consumption_feb = Decimal(str(rec.Electricity_Consumption_Feb))
                consumption_mar = Decimal(str(rec.Electricity_Consumption_Mar))
                
                ef_all = EmissionFactors.objects.filter(Type_of_Emission='Electricity').first()
                if type == "CO2E":
                    ef = Decimal(str(ef_all.CO2E_Emission_Factor))
                elif type == "CO2":
                    ef = Decimal(str(ef_all.CO2_Emission_Factor))
                
                emission_apr += ef * consumption_apr
                emission_may += ef * consumption_may
                emission_jun += ef * consumption_jun
                emission_jul += ef * consumption_jul
                emission_aug += ef * consumption_aug
                emission_sep += ef * consumption_sep
                emission_oct += ef * consumption_oct
                emission_nov += ef * consumption_nov
                emission_dec += ef * consumption_dec
                emission_jan += ef * consumption_jan
                emission_feb += ef * consumption_feb
                emission_mar += ef * consumption_mar
            
            record_json["Emission_Apr"] = round(float(emission_apr), 2)
            record_json["Emission_Apr"] = round(float(emission_apr), 2)
            record_json["Emission_May"] = round(float(emission_may), 2)
            record_json["Emission_Jun"] = round(float(emission_jun), 2)
            record_json["Emission_Jul"] = round(float(emission_jul), 2)
            record_json["Emission_Aug"] = round(float(emission_aug), 2)
            record_json["Emission_Sep"] = round(float(emission_sep), 2)
            record_json["Emission_Oct"] = round(float(emission_oct), 2)
            record_json["Emission_Nov"] = round(float(emission_nov), 2)
            record_json["Emission_Dec"] = round(float(emission_dec), 2)
            record_json["Emission_Jan"] = round(float(emission_jan), 2)
            record_json["Emission_Feb"] = round(float(emission_feb), 2)
            record_json["Emission_Mar"] = round(float(emission_mar), 2)
            record_json["Total_Emission"] = round(round(record_json['Emission_Apr'], 2) + round(record_json['Emission_May'], 2) + round(record_json['Emission_Jun'], 2) + round(record_json['Emission_Jul'], 2) + round(record_json['Emission_Aug'], 2) + round(record_json['Emission_Sep'], 2) + round(record_json['Emission_Oct'], 2) + round(record_json['Emission_Nov'], 2) + round(record_json['Emission_Dec'], 2) + round(record_json['Emission_Jan'], 2) + round(record_json['Emission_Feb'], 2) + round(record_json['Emission_Mar'], 2), 2)
            result.append(record_json)

    return result        



def calculate_scope_2_intensity():
    result = []
    from .models import Scope2_Emissions_by_Facilities
    from CompanyDetails.models import Turnover
    all_objects = Scope2_Emissions_by_Facilities.objects.all()
    for obj in all_objects:
        record_json = {}
        record_json["Financial_Year"] = obj.Financial_Year
        record_json["Facility"] = obj.Facility
        try:
            turnover = Turnover.objects.get(Financial_Year=record_json["Financial_Year"])
            turnover_apr = Decimal(turnover.Turnover_Apr.to_decimal())
            turnover_may = Decimal(turnover.Turnover_May.to_decimal())
            turnover_jun = Decimal(turnover.Turnover_Jun.to_decimal())
            turnover_jul = Decimal(turnover.Turnover_Jul.to_decimal())
            turnover_aug = Decimal(turnover.Turnover_Aug.to_decimal())
            turnover_sep = Decimal(turnover.Turnover_Sep.to_decimal())
            turnover_oct = Decimal(turnover.Turnover_Oct.to_decimal())
            turnover_nov = Decimal(turnover.Turnover_Nov.to_decimal())
            turnover_dec = Decimal(turnover.Turnover_Dec.to_decimal())
            turnover_jan = Decimal(turnover.Turnover_Jan.to_decimal())
            turnover_feb = Decimal(turnover.Turnover_Feb.to_decimal())
            turnover_mar = Decimal(turnover.Turnover_Mar.to_decimal())
            
            emission_apr = Decimal(obj.Emission_Apr.to_decimal())
            emission_may = Decimal(obj.Emission_May.to_decimal())
            emission_jun = Decimal(obj.Emission_Jun.to_decimal())
            emission_jul = Decimal(obj.Emission_Jul.to_decimal())
            emission_aug = Decimal(obj.Emission_Aug.to_decimal())
            emission_sep = Decimal(obj.Emission_Sep.to_decimal())
            emission_oct = Decimal(obj.Emission_Oct.to_decimal())
            emission_nov = Decimal(obj.Emission_Nov.to_decimal())
            emission_dec = Decimal(obj.Emission_Dec.to_decimal())
            emission_jan = Decimal(obj.Emission_Jan.to_decimal())
            emission_feb = Decimal(obj.Emission_Feb.to_decimal())
            emission_mar = Decimal(obj.Emission_Mar.to_decimal())

            record_json["Intensity_Apr"] = round(float(emission_apr / turnover_apr), 2) if turnover_apr > 0 else 0
            record_json["Intensity_May"] = round(float(emission_may / turnover_may), 2) if turnover_may > 0 else 0
            record_json["Intensity_Jun"] = round(float(emission_jun / turnover_jun), 2) if turnover_jun > 0 else 0
            record_json["Intensity_Jul"] = round(float(emission_jul / turnover_jul), 2) if turnover_jul > 0 else 0
            record_json["Intensity_Aug"] = round(float(emission_aug / turnover_aug), 2) if turnover_aug > 0 else 0
            record_json["Intensity_Sep"] = round(float(emission_sep / turnover_sep), 2) if turnover_sep > 0 else 0
            record_json["Intensity_Oct"] = round(float(emission_oct / turnover_oct), 2) if turnover_oct > 0 else 0
            record_json["Intensity_Nov"] = round(float(emission_nov / turnover_nov), 2) if turnover_nov > 0 else 0
            record_json["Intensity_Dec"] = round(float(emission_dec / turnover_dec), 2) if turnover_dec > 0 else 0
            record_json["Intensity_Jan"] = round(float(emission_jan / turnover_jan), 2) if turnover_jan > 0 else 0
            record_json["Intensity_Feb"] = round(float(emission_feb / turnover_feb), 2) if turnover_feb > 0 else 0
            record_json["Intensity_Mar"] = round(float(emission_mar / turnover_mar), 2) if turnover_mar > 0 else 0
            record_json["Total_Intensity"] = round(record_json["Intensity_Apr"] + record_json["Intensity_May"] + record_json["Intensity_Jun"] + record_json["Intensity_Jul"] + record_json["Intensity_Aug"] + record_json["Intensity_Sep"] + record_json["Intensity_Oct"] + record_json["Intensity_Nov"] + record_json["Intensity_Dec"] + record_json["Intensity_Jan"] + record_json["Intensity_Feb"] + record_json["Intensity_Mar"], 2)

            result.append(record_json)

        except Turnover.DoesNotExist:
            record_json["Intensity_Apr"] = 0
            record_json["Intensity_May"] = 0
            record_json["Intensity_Jun"] = 0
            record_json["Intensity_Jul"] = 0
            record_json["Intensity_Aug"] = 0
            record_json["Intensity_Sep"] = 0
            record_json["Intensity_Oct"] = 0
            record_json["Intensity_Nov"] = 0
            record_json["Intensity_Dec"] = 0
            record_json["Intensity_Jan"] = 0
            record_json["Intensity_Feb"] = 0
            record_json["Intensity_Mar"] = 0
            record_json["Total_Intensity"] = 0     
            result.append(record_json)   

    try:
        intensity_years = Scope2_Emissions_by_Facilities.objects.values_list('Financial_Year', flat=True).distinct()
        turnover_years = Turnover.objects.values_list('Financial_Year', flat=True)
        elements_in_list2_not_in_list1 = list(set(turnover_years) - set(intensity_years))
        for elem in elements_in_list2_not_in_list1:
            record_json = {}
            record_json["Financial_Year"] = elem
            record_json["Facility"] = "NA"
            record_json["Intensity_Apr"] = 0
            record_json["Intensity_May"] = 0
            record_json["Intensity_Jun"] = 0
            record_json["Intensity_Jul"] = 0
            record_json["Intensity_Aug"] = 0
            record_json["Intensity_Sep"] = 0
            record_json["Intensity_Oct"] = 0
            record_json["Intensity_Nov"] = 0
            record_json["Intensity_Dec"] = 0
            record_json["Intensity_Jan"] = 0
            record_json["Intensity_Feb"] = 0
            record_json["Intensity_Mar"] = 0
            record_json["Total_Intensity"] = 0
            result.append(record_json)
    except Exception as e:
        print(f"An error occurred: {e}")

    return result



def calculate_scope_3_emissions_fuel_onsite_vehicles_1():

    from .models import Fuel_Consumption_Onsite_Vehicles_General, EmissionFactors
    # Filter documents where ownership is 2 or 3
    filtered_documents = Fuel_Consumption_Onsite_Vehicles_General.objects.filter(Ownership__in=['Company owned and 3rd party controlled', '3rd party owned 3rd party controlled'])

    result = []
    # Print the filtered documents
    for document in filtered_documents:

        record_json = {}
        record_json["Financial_Year"] = document.Financial_Year
        record_json["Facility"] = document.Facility
        
        fuel_type = document.Fuel_Type
        unit = document.Unit
        ef_all = EmissionFactors.objects.filter(Type_of_Emission='Fuel', Fuel=fuel_type, Unit=unit).last()
        if ef_all:
            ef = ef_all.CO2E_Emission_Factor
            ef = Decimal128(str(ef))
            if ef:
                consumption_apr = Decimal128(str(document.Fuel_Consumption_Apr))
                consumption_may = Decimal128(str(document.Fuel_Consumption_May))
                consumption_jun = Decimal128(str(document.Fuel_Consumption_Jun))
                consumption_jul = Decimal128(str(document.Fuel_Consumption_Jul))
                consumption_aug = Decimal128(str(document.Fuel_Consumption_Aug))
                consumption_sep = Decimal128(str(document.Fuel_Consumption_Sep))
                consumption_oct = Decimal128(str(document.Fuel_Consumption_Oct))
                consumption_nov = Decimal128(str(document.Fuel_Consumption_Nov))
                consumption_dec = Decimal128(str(document.Fuel_Consumption_Dec))
                consumption_jan = Decimal128(str(document.Fuel_Consumption_Jan))
                consumption_feb = Decimal128(str(document.Fuel_Consumption_Feb))
                consumption_mar = Decimal128(str(document.Fuel_Consumption_Mar))
                            
                record_json["Emission_Apr"] = round(float(consumption_apr.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_May"] = round(float(consumption_may.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jun"] = round(float(consumption_jun.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jul"] = round(float(consumption_jul.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Aug"] = round(float(consumption_aug.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Sep"] = round(float(consumption_sep.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Oct"] = round(float(consumption_oct.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Nov"] = round(float(consumption_nov.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Dec"] = round(float(consumption_dec.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jan"] = round(float(consumption_jan.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Feb"] = round(float(consumption_feb.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Mar"] = round(float(consumption_mar.to_decimal()) * float(ef.to_decimal()), 2)

                result.append(record_json)

    return result



def calculate_scope_3_emissions_fuel_consumption_inbound_logistics_1():
    from .models import Inbound_Logistics, EmissionFactors

    # Filter documents where ownership is 2 or 3
    filtered_documents = Inbound_Logistics.objects.filter(Ownership__in=['Company owned and 3rd party controlled', '3rd party owned 3rd party controlled'])

    result = []
    # Print the filtered documents
    for document in filtered_documents:

        record_json = {}
        record_json["Financial_Year"] = document.Financial_Year
        record_json["Facility"] = document.Facility
        
        ef_all = EmissionFactors.objects.filter(Type_of_Emission='Logistics', Mode=document.Fuel_Type).last()
        if ef_all:
            ef = ef_all.CO2_Emission_Factor
            ef = Decimal128(str(ef))
            if ef:
                consumption_apr = Decimal128(str(document.Fuel_Consumption_Apr))
                consumption_may = Decimal128(str(document.Fuel_Consumption_May))
                consumption_jun = Decimal128(str(document.Fuel_Consumption_Jun))
                consumption_jul = Decimal128(str(document.Fuel_Consumption_Jul))
                consumption_aug = Decimal128(str(document.Fuel_Consumption_Aug))
                consumption_sep = Decimal128(str(document.Fuel_Consumption_Sep))
                consumption_oct = Decimal128(str(document.Fuel_Consumption_Oct))
                consumption_nov = Decimal128(str(document.Fuel_Consumption_Nov))
                consumption_dec = Decimal128(str(document.Fuel_Consumption_Dec))
                consumption_jan = Decimal128(str(document.Fuel_Consumption_Jan))
                consumption_feb = Decimal128(str(document.Fuel_Consumption_Feb))
                consumption_mar = Decimal128(str(document.Fuel_Consumption_Mar))
                            
                record_json["Emission_Apr"] = round(float(consumption_apr.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_May"] = round(float(consumption_may.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jun"] = round(float(consumption_jun.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jul"] = round(float(consumption_jul.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Aug"] = round(float(consumption_aug.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Sep"] = round(float(consumption_sep.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Oct"] = round(float(consumption_oct.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Nov"] = round(float(consumption_nov.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Dec"] = round(float(consumption_dec.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jan"] = round(float(consumption_jan.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Feb"] = round(float(consumption_feb.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Mar"] = round(float(consumption_mar.to_decimal()) * float(ef.to_decimal()), 2)

                result.append(record_json)

    return result



def calculate_scope_3_emissions_fuel_consumption_outbound_logistics_1():
    from .models import Outbound_Logistics, EmissionFactors
    # Filter documents where ownership is 2 or 3
    filtered_documents = Outbound_Logistics.objects.filter(Ownership__in=['Company owned and 3rd party controlled', '3rd party owned 3rd party controlled'])

    result = []
    # Print the filtered documents
    for document in filtered_documents:

        record_json = {}
        record_json["Financial_Year"] = document.Financial_Year
        record_json["Facility"] = document.Facility
        
        ef_all = EmissionFactors.objects.filter(Type_of_Emission='Logistics', Mode=document.Fuel_Type).last()
        if ef_all:
            ef = ef_all.CO2_Emission_Factor
            ef = Decimal128(str(ef))
            if ef:
                consumption_apr = Decimal128(str(document.Fuel_Consumption_Apr))
                consumption_may = Decimal128(str(document.Fuel_Consumption_May))
                consumption_jun = Decimal128(str(document.Fuel_Consumption_Jun))
                consumption_jul = Decimal128(str(document.Fuel_Consumption_Jul))
                consumption_aug = Decimal128(str(document.Fuel_Consumption_Aug))
                consumption_sep = Decimal128(str(document.Fuel_Consumption_Sep))
                consumption_oct = Decimal128(str(document.Fuel_Consumption_Oct))
                consumption_nov = Decimal128(str(document.Fuel_Consumption_Nov))
                consumption_dec = Decimal128(str(document.Fuel_Consumption_Dec))
                consumption_jan = Decimal128(str(document.Fuel_Consumption_Jan))
                consumption_feb = Decimal128(str(document.Fuel_Consumption_Feb))
                consumption_mar = Decimal128(str(document.Fuel_Consumption_Mar))
                            
                record_json["Emission_Apr"] = round(float(consumption_apr.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_May"] = round(float(consumption_may.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jun"] = round(float(consumption_jun.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jul"] = round(float(consumption_jul.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Aug"] = round(float(consumption_aug.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Sep"] = round(float(consumption_sep.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Oct"] = round(float(consumption_oct.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Nov"] = round(float(consumption_nov.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Dec"] = round(float(consumption_dec.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jan"] = round(float(consumption_jan.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Feb"] = round(float(consumption_feb.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Mar"] = round(float(consumption_mar.to_decimal()) * float(ef.to_decimal()), 2)

                result.append(record_json)

    return result



def calculate_scope_3_emissions_fuel_consumption_employee_commuting_1():
    from .models import Employee_Commuting, EmissionFactors

    filtered_documents = Employee_Commuting.objects.all()

    result = []
    # Print the filtered documents
    for document in filtered_documents:

        record_json = {}
        record_json["Financial_Year"] = document.Financial_Year
        record_json["Facility"] = document.Facility

        if document.Commute_to_Work == "Public Transport":

            if document.Type_of_Transport == "By Metro" or document.Type_of_Transport == "By Company Bus":
                ef_all = EmissionFactors.objects.filter(Type_of_Emission='Transport', 
                                                    Type_of_Transport=document.Type_of_Transport).last()
            else:
                ef_all = EmissionFactors.objects.filter(Type_of_Emission='Transport', 
                                                    Type_of_Transport=document.Type_of_Transport,
                                                    Type_of_Vehicle=document.Vehicle_Type).last()
        elif document.Commute_to_Work == "Personal Vehicle":
            ef_all = EmissionFactors.objects.filter(Type_of_Emission='Transport', 
                                                 Type_of_Transport=document.Type_of_Transport,
                                                 Type_of_Vehicle=document.Vehicle_Type,
                                                 Fuel=document.Fuel_Type).last()
        
        if ef_all:
            ef = ef_all.CO2E_Emission_Factor
            ef = Decimal128(str(ef))
            if ef:
                consumption_apr = Decimal128(str(document.Fuel_Consumption_Apr))
                consumption_may = Decimal128(str(document.Fuel_Consumption_May))
                consumption_jun = Decimal128(str(document.Fuel_Consumption_Jun))
                consumption_jul = Decimal128(str(document.Fuel_Consumption_Jul))
                consumption_aug = Decimal128(str(document.Fuel_Consumption_Aug))
                consumption_sep = Decimal128(str(document.Fuel_Consumption_Sep))
                consumption_oct = Decimal128(str(document.Fuel_Consumption_Oct))
                consumption_nov = Decimal128(str(document.Fuel_Consumption_Nov))
                consumption_dec = Decimal128(str(document.Fuel_Consumption_Dec))
                consumption_jan = Decimal128(str(document.Fuel_Consumption_Jan))
                consumption_feb = Decimal128(str(document.Fuel_Consumption_Feb))
                consumption_mar = Decimal128(str(document.Fuel_Consumption_Mar))
                            
                record_json["Emission_Apr"] = round(float(consumption_apr.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_May"] = round(float(consumption_may.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jun"] = round(float(consumption_jun.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jul"] = round(float(consumption_jul.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Aug"] = round(float(consumption_aug.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Sep"] = round(float(consumption_sep.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Oct"] = round(float(consumption_oct.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Nov"] = round(float(consumption_nov.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Dec"] = round(float(consumption_dec.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jan"] = round(float(consumption_jan.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Feb"] = round(float(consumption_feb.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Mar"] = round(float(consumption_mar.to_decimal()) * float(ef.to_decimal()), 2)

                result.append(record_json)

    return result



def calculate_scope_3_emissions_fuel_consumption_business_travel_1():
    from .models import Business_Travel, EmissionFactors

    filtered_documents = Business_Travel.objects.all()

    result = []
    # Print the filtered documents
    for document in filtered_documents:

        record_json = {}
        record_json["Financial_Year"] = document.Financial_Year
        record_json["Facility"] = document.Facility

        ef_all = EmissionFactors.objects.filter(Type_of_Emission='Business Travel',
                                             Type_of_Transport=document.Mode).last()
        if ef_all:
            ef = ef_all.CO2E_Emission_Factor
            ef = Decimal128(str(ef))
            if ef:
                consumption_apr = Decimal128(str(document.Fuel_Consumption_Apr))
                consumption_may = Decimal128(str(document.Fuel_Consumption_May))
                consumption_jun = Decimal128(str(document.Fuel_Consumption_Jun))
                consumption_jul = Decimal128(str(document.Fuel_Consumption_Jul))
                consumption_aug = Decimal128(str(document.Fuel_Consumption_Aug))
                consumption_sep = Decimal128(str(document.Fuel_Consumption_Sep))
                consumption_oct = Decimal128(str(document.Fuel_Consumption_Oct))
                consumption_nov = Decimal128(str(document.Fuel_Consumption_Nov))
                consumption_dec = Decimal128(str(document.Fuel_Consumption_Dec))
                consumption_jan = Decimal128(str(document.Fuel_Consumption_Jan))
                consumption_feb = Decimal128(str(document.Fuel_Consumption_Feb))
                consumption_mar = Decimal128(str(document.Fuel_Consumption_Mar))
                            
                record_json["Emission_Apr"] = round(float(consumption_apr.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_May"] = round(float(consumption_may.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jun"] = round(float(consumption_jun.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jul"] = round(float(consumption_jul.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Aug"] = round(float(consumption_aug.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Sep"] = round(float(consumption_sep.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Oct"] = round(float(consumption_oct.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Nov"] = round(float(consumption_nov.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Dec"] = round(float(consumption_dec.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Jan"] = round(float(consumption_jan.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Feb"] = round(float(consumption_feb.to_decimal()) * float(ef.to_decimal()), 2)
                record_json["Emission_Mar"] = round(float(consumption_mar.to_decimal()) * float(ef.to_decimal()), 2)

                result.append(record_json)

    return result


def calculate_scope_3_emissions_by_facilities():
    onsite_vehicles_list = calculate_scope_3_emissions_fuel_onsite_vehicles_1()
    inbound_logistics_list = calculate_scope_3_emissions_fuel_consumption_inbound_logistics_1()
    outbound_logistics_list = calculate_scope_3_emissions_fuel_consumption_outbound_logistics_1()
    business_travel_list = calculate_scope_3_emissions_fuel_consumption_business_travel_1()
    employee_commuting_list = calculate_scope_3_emissions_fuel_consumption_employee_commuting_1()

    combined_list = onsite_vehicles_list + inbound_logistics_list + outbound_logistics_list + business_travel_list + employee_commuting_list
    
    # Create a dictionary to store the aggregated results
    result_dict = {}
    # Process the combined list to sum emissions for the same Financial_Year and Facility
    for data in combined_list:
        key = (data['Financial_Year'], data['Facility'])
        if key not in result_dict:
            result_dict[key] = {
                'Financial_Year': data['Financial_Year'],
                'Facility': data['Facility'],
                'Emission_Apr': round(data['Emission_Apr'], 2),
                'Emission_May': round(data['Emission_May'], 2),
                'Emission_Jun': round(data['Emission_Jun'], 2),
                'Emission_Jul': round(data['Emission_Jul'], 2),
                'Emission_Aug': round(data['Emission_Aug'], 2),
                'Emission_Sep': round(data['Emission_Sep'], 2),
                'Emission_Oct': round(data['Emission_Oct'], 2),
                'Emission_Nov': round(data['Emission_Nov'], 2),
                'Emission_Dec': round(data['Emission_Dec'], 2),
                'Emission_Jan': round(data['Emission_Jan'], 2),
                'Emission_Feb': round(data['Emission_Feb'], 2),
                'Emission_Mar': round(data['Emission_Mar'], 2),
                'Total_Emission': round(
                    data['Emission_Apr'] + data['Emission_May'] + data['Emission_Jun'] + 
                    data['Emission_Jul'] + data['Emission_Aug'] + data['Emission_Sep'] + 
                    data['Emission_Oct'] + data['Emission_Nov'] + data['Emission_Dec'] + 
                    data['Emission_Jan'] + data['Emission_Feb'] + data['Emission_Mar'], 2)
            }
        else:
            result_dict[key]['Emission_Apr'] = round(result_dict[key]['Emission_Apr'] + data['Emission_Apr'], 2)
            result_dict[key]['Emission_May'] = round(result_dict[key]['Emission_May'] + data['Emission_May'], 2)
            result_dict[key]['Emission_Jun'] = round(result_dict[key]['Emission_Jun'] + data['Emission_Jun'], 2)
            result_dict[key]['Emission_Jul'] = round(result_dict[key]['Emission_Jul'] + data['Emission_Jul'], 2)
            result_dict[key]['Emission_Aug'] = round(result_dict[key]['Emission_Aug'] + data['Emission_Aug'], 2)
            result_dict[key]['Emission_Sep'] = round(result_dict[key]['Emission_Sep'] + data['Emission_Sep'], 2)
            result_dict[key]['Emission_Oct'] = round(result_dict[key]['Emission_Oct'] + data['Emission_Oct'], 2)
            result_dict[key]['Emission_Nov'] = round(result_dict[key]['Emission_Nov'] + data['Emission_Nov'], 2)
            result_dict[key]['Emission_Dec'] = round(result_dict[key]['Emission_Dec'] + data['Emission_Dec'], 2)
            result_dict[key]['Emission_Jan'] = round(result_dict[key]['Emission_Jan'] + data['Emission_Jan'], 2)
            result_dict[key]['Emission_Feb'] = round(result_dict[key]['Emission_Feb'] + data['Emission_Feb'], 2)
            result_dict[key]['Emission_Mar'] = round(result_dict[key]['Emission_Mar'] + data['Emission_Mar'], 2)
            result_dict[key]['Total_Emission'] = round(
                result_dict[key]['Emission_Apr'] + result_dict[key]['Emission_May'] + result_dict[key]['Emission_Jun'] + 
                result_dict[key]['Emission_Jul'] + result_dict[key]['Emission_Aug'] + result_dict[key]['Emission_Sep'] + 
                result_dict[key]['Emission_Oct'] + result_dict[key]['Emission_Nov'] + result_dict[key]['Emission_Dec'] + 
                result_dict[key]['Emission_Jan'] + result_dict[key]['Emission_Feb'] + result_dict[key]['Emission_Mar'], 2)


    # Convert the result dictionary to a list
    final_result = list(result_dict.values())

    return final_result



def calculate_scope_3_emissions_fuel_onsite_vehicles_2():
    # Get distinct financial years
    from .models import Fuel_Consumption_Onsite_Vehicles_General
    distinct_years = Fuel_Consumption_Onsite_Vehicles_General.objects.filter(
        Ownership__in=['Company owned and 3rd party controlled', '3rd party owned 3rd party controlled']
    ).values_list('Financial_Year', flat=True).distinct()

    result = []

    def convert_decimal128_to_float(value):
        """Helper function to convert Decimal128 to float."""
        if isinstance(value, Decimal128):
            return float(value.to_decimal())
        return float(value or 0)

    for year in distinct_years:
        # Initialize the record for each year
        record_json = {
            "Financial_Year": year,
            "Activity": "Onsite Vehicles",
            "Emission_Apr": 0.0,
            "Emission_May": 0.0,
            "Emission_Jun": 0.0,
            "Emission_Jul": 0.0,
            "Emission_Aug": 0.0,
            "Emission_Sep": 0.0,
            "Emission_Oct": 0.0,
            "Emission_Nov": 0.0,
            "Emission_Dec": 0.0,
            "Emission_Jan": 0.0,
            "Emission_Feb": 0.0,
            "Emission_Mar": 0.0,
            "Total_Emission": 0.0
        }

        # Filter documents for the given year and specified ownership types
        filtered_documents = Fuel_Consumption_Onsite_Vehicles_General.objects.filter(
            Ownership__in=['Company owned and 3rd party controlled', '3rd party owned 3rd party controlled'],
            Financial_Year=year
        )

        # Accumulate emissions for each month
        for document in filtered_documents:
            record_json["Emission_Apr"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Apr), 2)
            record_json["Emission_May"] += round(convert_decimal128_to_float(document.Fuel_Consumption_May), 2)
            record_json["Emission_Jun"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jun), 2)
            record_json["Emission_Jul"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jul), 2)
            record_json["Emission_Aug"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Aug), 2)
            record_json["Emission_Sep"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Sep), 2)
            record_json["Emission_Oct"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Oct), 2)
            record_json["Emission_Nov"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Nov), 2)
            record_json["Emission_Dec"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Dec), 2)
            record_json["Emission_Jan"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jan), 2)
            record_json["Emission_Feb"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Feb), 2)
            record_json["Emission_Mar"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Mar), 2)
        
        # Calculate total emission and round to 2 decimal places
        total_emission = sum(
            record_json[month] for month in ["Emission_Apr", "Emission_May", "Emission_Jun", "Emission_Jul", 
                                             "Emission_Aug", "Emission_Sep", "Emission_Oct", "Emission_Nov", 
                                             "Emission_Dec", "Emission_Jan", "Emission_Feb", "Emission_Mar"]
        )
        record_json["Total_Emission"] = round(total_emission, 2)

        # Round emission values to 2 decimal places
        for month in ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]:
            record_json[f"Emission_{month}"] = round(record_json[f"Emission_{month}"], 2)

        # Append the record to results
        result.append(record_json)

    return result




def calculate_scope_3_emissions_fuel_consumption_inbound_logistics_2():

    # Get distinct financial years
    from .models import Inbound_Logistics
    distinct_years = Inbound_Logistics.objects.filter(
        Ownership__in=['Company owned and 3rd party controlled', '3rd party owned 3rd party controlled']
    ).values_list('Financial_Year', flat=True).distinct()

    result = []

    def convert_decimal128_to_float(value):
        """Helper function to convert Decimal128 to float."""
        if isinstance(value, Decimal128):
            return float(value.to_decimal())
        return float(value or 0)

    for year in distinct_years:
        # Initialize the record for each year
        record_json = {
            "Financial_Year": year,
            "Activity": "Inbound Logistics",
            "Emission_Apr": 0.0,
            "Emission_May": 0.0,
            "Emission_Jun": 0.0,
            "Emission_Jul": 0.0,
            "Emission_Aug": 0.0,
            "Emission_Sep": 0.0,
            "Emission_Oct": 0.0,
            "Emission_Nov": 0.0,
            "Emission_Dec": 0.0,
            "Emission_Jan": 0.0,
            "Emission_Feb": 0.0,
            "Emission_Mar": 0.0,
            "Total_Emission": 0.0
        }

        # Filter documents for the given year and specified ownership types
        filtered_documents = Inbound_Logistics.objects.filter(
            Ownership__in=['Company owned and 3rd party controlled', '3rd party owned 3rd party controlled'],
            Financial_Year=year
        )

        # Accumulate emissions for each month
        for document in filtered_documents:
            record_json["Emission_Apr"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Apr), 2)
            record_json["Emission_May"] += round(convert_decimal128_to_float(document.Fuel_Consumption_May), 2)
            record_json["Emission_Jun"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jun), 2)
            record_json["Emission_Jul"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jul), 2)
            record_json["Emission_Aug"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Aug), 2)
            record_json["Emission_Sep"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Sep), 2)
            record_json["Emission_Oct"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Oct), 2)
            record_json["Emission_Nov"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Nov), 2)
            record_json["Emission_Dec"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Dec), 2)
            record_json["Emission_Jan"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jan), 2)
            record_json["Emission_Feb"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Feb), 2)
            record_json["Emission_Mar"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Mar), 2)
        
        # Calculate total emission and round to 2 decimal places
        total_emission = sum(
            record_json[month] for month in ["Emission_Apr", "Emission_May", "Emission_Jun", "Emission_Jul", 
                                             "Emission_Aug", "Emission_Sep", "Emission_Oct", "Emission_Nov", 
                                             "Emission_Dec", "Emission_Jan", "Emission_Feb", "Emission_Mar"]
        )
        record_json["Total_Emission"] = round(total_emission, 2)

        # Round emission values to 2 decimal places
        for month in ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]:
            record_json[f"Emission_{month}"] = round(record_json[f"Emission_{month}"], 2)

        # Append the record to results
        result.append(record_json)

    return result



def calculate_scope_3_emissions_fuel_consumption_outbound_logistics_2():
    from .models import Outbound_Logistics
    # Get distinct financial years
    distinct_years = Outbound_Logistics.objects.filter(
        Ownership__in=['Company owned and 3rd party controlled', '3rd party owned 3rd party controlled']
    ).values_list('Financial_Year', flat=True).distinct()

    result = []

    def convert_decimal128_to_float(value):
        """Helper function to convert Decimal128 to float."""
        if isinstance(value, Decimal128):
            return float(value.to_decimal())
        return float(value or 0)

    for year in distinct_years:
        # Initialize the record for each year
        record_json = {
            "Financial_Year": year,
            "Activity": "Outbound Logistics",
            "Emission_Apr": 0.0,
            "Emission_May": 0.0,
            "Emission_Jun": 0.0,
            "Emission_Jul": 0.0,
            "Emission_Aug": 0.0,
            "Emission_Sep": 0.0,
            "Emission_Oct": 0.0,
            "Emission_Nov": 0.0,
            "Emission_Dec": 0.0,
            "Emission_Jan": 0.0,
            "Emission_Feb": 0.0,
            "Emission_Mar": 0.0,
            "Total_Emission": 0.0
        }

        # Filter documents for the given year and specified ownership types
        filtered_documents = Outbound_Logistics.objects.filter(
            Ownership__in=['Company owned and 3rd party controlled', '3rd party owned 3rd party controlled'],
            Financial_Year=year
        )

        # Accumulate emissions for each month
        for document in filtered_documents:
            record_json["Emission_Apr"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Apr), 2)
            record_json["Emission_May"] += round(convert_decimal128_to_float(document.Fuel_Consumption_May), 2)
            record_json["Emission_Jun"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jun), 2)
            record_json["Emission_Jul"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jul), 2)
            record_json["Emission_Aug"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Aug), 2)
            record_json["Emission_Sep"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Sep), 2)
            record_json["Emission_Oct"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Oct), 2)
            record_json["Emission_Nov"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Nov), 2)
            record_json["Emission_Dec"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Dec), 2)
            record_json["Emission_Jan"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jan), 2)
            record_json["Emission_Feb"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Feb), 2)
            record_json["Emission_Mar"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Mar), 2)
        
        # Calculate total emission and round to 2 decimal places
        total_emission = sum(
            record_json[month] for month in ["Emission_Apr", "Emission_May", "Emission_Jun", "Emission_Jul", 
                                             "Emission_Aug", "Emission_Sep", "Emission_Oct", "Emission_Nov", 
                                             "Emission_Dec", "Emission_Jan", "Emission_Feb", "Emission_Mar"]
        )
        record_json["Total_Emission"] = round(total_emission, 2)

        # Round emission values to 2 decimal places
        for month in ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]:
            record_json[f"Emission_{month}"] = round(record_json[f"Emission_{month}"], 2)

        # Append the record to results
        result.append(record_json)

    return result



def calculate_scope_3_emissions_fuel_consumption_business_travel_2():
    from .models import Business_Travel
    # Get distinct financial years
    distinct_years = Business_Travel.objects.values_list('Financial_Year', flat=True).distinct()

    result = []

    def convert_decimal128_to_float(value):
        """Helper function to convert Decimal128 to float."""
        if isinstance(value, Decimal128):
            return float(value.to_decimal())
        return float(value or 0)

    for year in distinct_years:
        # Initialize the record for each year
        record_json = {
            "Financial_Year": year,
            "Activity": "Business Travel",
            "Emission_Apr": 0.0,
            "Emission_May": 0.0,
            "Emission_Jun": 0.0,
            "Emission_Jul": 0.0,
            "Emission_Aug": 0.0,
            "Emission_Sep": 0.0,
            "Emission_Oct": 0.0,
            "Emission_Nov": 0.0,
            "Emission_Dec": 0.0,
            "Emission_Jan": 0.0,
            "Emission_Feb": 0.0,
            "Emission_Mar": 0.0,
            "Total_Emission": 0.0
        }

        # Filter documents for the given year and specified ownership types
        filtered_documents = Business_Travel.objects.filter(
            Financial_Year=year
        )

        # Accumulate emissions for each month
        for document in filtered_documents:
            record_json["Emission_Apr"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Apr), 2)
            record_json["Emission_May"] += round(convert_decimal128_to_float(document.Fuel_Consumption_May), 2)
            record_json["Emission_Jun"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jun), 2)
            record_json["Emission_Jul"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jul), 2)
            record_json["Emission_Aug"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Aug), 2)
            record_json["Emission_Sep"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Sep), 2)
            record_json["Emission_Oct"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Oct), 2)
            record_json["Emission_Nov"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Nov), 2)
            record_json["Emission_Dec"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Dec), 2)
            record_json["Emission_Jan"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jan), 2)
            record_json["Emission_Feb"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Feb), 2)
            record_json["Emission_Mar"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Mar), 2)
        
        # Calculate total emission and round to 2 decimal places
        total_emission = sum(
            record_json[month] for month in ["Emission_Apr", "Emission_May", "Emission_Jun", "Emission_Jul", 
                                             "Emission_Aug", "Emission_Sep", "Emission_Oct", "Emission_Nov", 
                                             "Emission_Dec", "Emission_Jan", "Emission_Feb", "Emission_Mar"]
        )
        record_json["Total_Emission"] = round(total_emission, 2)

        # Round emission values to 2 decimal places
        for month in ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]:
            record_json[f"Emission_{month}"] = round(record_json[f"Emission_{month}"], 2)

        # Append the record to results
        result.append(record_json)

    return result



def calculate_scope_3_emissions_fuel_consumption_employee_commuting_2():

    # Get distinct financial years
    from .models import Employee_Commuting
    distinct_years = Employee_Commuting.objects.values_list('Financial_Year', flat=True).distinct()

    result = []

    def convert_decimal128_to_float(value):
        """Helper function to convert Decimal128 to float."""
        if isinstance(value, Decimal128):
            return float(value.to_decimal())
        return float(value or 0)

    for year in distinct_years:
        # Initialize the record for each year
        record_json = {
            "Financial_Year": year,
            "Activity": "Employee Commuting",
            "Emission_Apr": 0.0,
            "Emission_May": 0.0,
            "Emission_Jun": 0.0,
            "Emission_Jul": 0.0,
            "Emission_Aug": 0.0,
            "Emission_Sep": 0.0,
            "Emission_Oct": 0.0,
            "Emission_Nov": 0.0,
            "Emission_Dec": 0.0,
            "Emission_Jan": 0.0,
            "Emission_Feb": 0.0,
            "Emission_Mar": 0.0,
            "Total_Emission": 0.0
        }

        # Filter documents for the given year and specified ownership types
        filtered_documents = Employee_Commuting.objects.filter(
            Financial_Year=year
        )

        # Accumulate emissions for each month
        for document in filtered_documents:
            record_json["Emission_Apr"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Apr), 2)
            record_json["Emission_May"] += round(convert_decimal128_to_float(document.Fuel_Consumption_May), 2)
            record_json["Emission_Jun"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jun), 2)
            record_json["Emission_Jul"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jul), 2)
            record_json["Emission_Aug"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Aug), 2)
            record_json["Emission_Sep"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Sep), 2)
            record_json["Emission_Oct"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Oct), 2)
            record_json["Emission_Nov"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Nov), 2)
            record_json["Emission_Dec"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Dec), 2)
            record_json["Emission_Jan"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Jan), 2)
            record_json["Emission_Feb"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Feb), 2)
            record_json["Emission_Mar"] += round(convert_decimal128_to_float(document.Fuel_Consumption_Mar), 2)
        
        # Calculate total emission and round to 2 decimal places
        total_emission = sum(
            record_json[month] for month in ["Emission_Apr", "Emission_May", "Emission_Jun", "Emission_Jul", 
                                             "Emission_Aug", "Emission_Sep", "Emission_Oct", "Emission_Nov", 
                                             "Emission_Dec", "Emission_Jan", "Emission_Feb", "Emission_Mar"]
        )
        record_json["Total_Emission"] = round(total_emission, 2)

        # Round emission values to 2 decimal places
        for month in ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]:
            record_json[f"Emission_{month}"] = round(record_json[f"Emission_{month}"], 2)

        # Append the record to results
        result.append(record_json)

    return result



def calculate_scope_3_emissions_by_activity():

    onsite_vehicles_list = calculate_scope_3_emissions_fuel_onsite_vehicles_2()
    inbound_logistics_list = calculate_scope_3_emissions_fuel_consumption_inbound_logistics_2()
    outbound_logistics_list = calculate_scope_3_emissions_fuel_consumption_outbound_logistics_2()
    business_travel_list = calculate_scope_3_emissions_fuel_consumption_business_travel_2()
    employee_commuting_list = calculate_scope_3_emissions_fuel_consumption_employee_commuting_2()

    # Concatenate the lists using the + operator
    result_list = onsite_vehicles_list+inbound_logistics_list+outbound_logistics_list+business_travel_list+employee_commuting_list

    return result_list


def calculate_scope_3_emissions_by_ghg_type():

    # Get distinct financial years
    from .models import Scope3_Emissions_by_Facilities
    distinct_years = Scope3_Emissions_by_Facilities.objects.values_list('Financial_Year', flat=True).distinct()

    result = []

    def convert_decimal128_to_float(value):
        """Helper function to convert Decimal128 to float."""
        if isinstance(value, Decimal128):
            return float(value.to_decimal())
        return float(value or 0)

    for year in distinct_years:
        # Initialize the record for each year
        record_json = {
            "Financial_Year": year,
            "GHG_Type": "CO2E",
            "Emission_Apr": 0.0,
            "Emission_May": 0.0,
            "Emission_Jun": 0.0,
            "Emission_Jul": 0.0,
            "Emission_Aug": 0.0,
            "Emission_Sep": 0.0,
            "Emission_Oct": 0.0,
            "Emission_Nov": 0.0,
            "Emission_Dec": 0.0,
            "Emission_Jan": 0.0,
            "Emission_Feb": 0.0,
            "Emission_Mar": 0.0,
            "Total_Emission": 0.0
        }

        # Filter documents for the given year and specified ownership types
        filtered_documents = Scope3_Emissions_by_Facilities.objects.filter(
            Financial_Year=year
        )

        # Accumulate emissions for each month
        for document in filtered_documents:
            record_json["Emission_Apr"] += round(convert_decimal128_to_float(document.Emission_Apr), 2)
            record_json["Emission_May"] += round(convert_decimal128_to_float(document.Emission_May), 2)
            record_json["Emission_Jun"] += round(convert_decimal128_to_float(document.Emission_Jun), 2)
            record_json["Emission_Jul"] += round(convert_decimal128_to_float(document.Emission_Jul), 2)
            record_json["Emission_Aug"] += round(convert_decimal128_to_float(document.Emission_Aug), 2)
            record_json["Emission_Sep"] += round(convert_decimal128_to_float(document.Emission_Sep), 2)
            record_json["Emission_Oct"] += round(convert_decimal128_to_float(document.Emission_Oct), 2)
            record_json["Emission_Nov"] += round(convert_decimal128_to_float(document.Emission_Nov), 2)
            record_json["Emission_Dec"] += round(convert_decimal128_to_float(document.Emission_Dec), 2)
            record_json["Emission_Jan"] += round(convert_decimal128_to_float(document.Emission_Jan), 2)
            record_json["Emission_Feb"] += round(convert_decimal128_to_float(document.Emission_Feb), 2)
            record_json["Emission_Mar"] += round(convert_decimal128_to_float(document.Emission_Mar), 2)
        
        # Calculate total emission and round to 2 decimal places
        total_emission = sum(
            record_json[month] for month in ["Emission_Apr", "Emission_May", "Emission_Jun", "Emission_Jul", 
                                             "Emission_Aug", "Emission_Sep", "Emission_Oct", "Emission_Nov", 
                                             "Emission_Dec", "Emission_Jan", "Emission_Feb", "Emission_Mar"]
        )
        record_json["Total_Emission"] = round(total_emission, 2)

        # Round emission values to 2 decimal places
        for month in ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]:
            record_json[f"Emission_{month}"] = round(record_json[f"Emission_{month}"], 2)

        # Append the record to results
        result.append(record_json)

    return result




def calculate_scope_3_intensity():
    from .models import Scope3_Emissions_by_Facilities
    from CompanyDetails.models import Turnover
    result = []
    all_objects = Scope3_Emissions_by_Facilities.objects.all()
    for obj in all_objects:
        record_json = {}
        record_json["Financial_Year"] = obj.Financial_Year
        record_json["Facility"] = obj.Facility
        try:
            turnover = Turnover.objects.filter(Financial_Year=record_json["Financial_Year"]).last()
            if turnover:
                turnover_apr = Decimal(turnover.Turnover_Apr.to_decimal())
                turnover_may = Decimal(turnover.Turnover_May.to_decimal())
                turnover_jun = Decimal(turnover.Turnover_Jun.to_decimal())
                turnover_jul = Decimal(turnover.Turnover_Jul.to_decimal())
                turnover_aug = Decimal(turnover.Turnover_Aug.to_decimal())
                turnover_sep = Decimal(turnover.Turnover_Sep.to_decimal())
                turnover_oct = Decimal(turnover.Turnover_Oct.to_decimal())
                turnover_nov = Decimal(turnover.Turnover_Nov.to_decimal())
                turnover_dec = Decimal(turnover.Turnover_Dec.to_decimal())
                turnover_jan = Decimal(turnover.Turnover_Jan.to_decimal())
                turnover_feb = Decimal(turnover.Turnover_Feb.to_decimal())
                turnover_mar = Decimal(turnover.Turnover_Mar.to_decimal())
                
                emission_apr = Decimal(obj.Emission_Apr.to_decimal())
                emission_may = Decimal(obj.Emission_May.to_decimal())
                emission_jun = Decimal(obj.Emission_Jun.to_decimal())
                emission_jul = Decimal(obj.Emission_Jul.to_decimal())
                emission_aug = Decimal(obj.Emission_Aug.to_decimal())
                emission_sep = Decimal(obj.Emission_Sep.to_decimal())
                emission_oct = Decimal(obj.Emission_Oct.to_decimal())
                emission_nov = Decimal(obj.Emission_Nov.to_decimal())
                emission_dec = Decimal(obj.Emission_Dec.to_decimal())
                emission_jan = Decimal(obj.Emission_Jan.to_decimal())
                emission_feb = Decimal(obj.Emission_Feb.to_decimal())
                emission_mar = Decimal(obj.Emission_Mar.to_decimal())

                record_json["Intensity_Apr"] = round(float(emission_apr / turnover_apr), 2) if turnover_apr else 0
                record_json["Intensity_May"] = round(float(emission_may / turnover_may), 2) if turnover_may else 0
                record_json["Intensity_Jun"] = round(float(emission_jun / turnover_jun), 2) if turnover_jun else 0
                record_json["Intensity_Jul"] = round(float(emission_jul / turnover_jul), 2) if turnover_jul else 0
                record_json["Intensity_Aug"] = round(float(emission_aug / turnover_aug), 2) if turnover_aug else 0
                record_json["Intensity_Sep"] = round(float(emission_sep / turnover_sep), 2) if turnover_sep else 0
                record_json["Intensity_Oct"] = round(float(emission_oct / turnover_oct), 2) if turnover_oct else 0
                record_json["Intensity_Nov"] = round(float(emission_nov / turnover_nov), 2) if turnover_nov else 0
                record_json["Intensity_Dec"] = round(float(emission_dec / turnover_dec), 2) if turnover_dec else 0
                record_json["Intensity_Jan"] = round(float(emission_jan / turnover_jan), 2) if turnover_jan else 0
                record_json["Intensity_Feb"] = round(float(emission_feb / turnover_feb), 2) if turnover_feb else 0
                record_json["Intensity_Mar"] = round(float(emission_mar / turnover_mar), 2) if turnover_mar else 0
                record_json["Total_Intensity"] = round(record_json["Intensity_Apr"] + record_json["Intensity_May"] + record_json["Intensity_Jun"] + record_json["Intensity_Jul"] + record_json["Intensity_Aug"] + record_json["Intensity_Sep"] + record_json["Intensity_Oct"] + record_json["Intensity_Nov"] + record_json["Intensity_Dec"] + record_json["Intensity_Jan"] + record_json["Intensity_Feb"] + record_json["Intensity_Mar"], 2)

                result.append(record_json)

        except Turnover.DoesNotExist:
            record_json["Intensity_Apr"] = 0
            record_json["Intensity_May"] = 0
            record_json["Intensity_Jun"] = 0
            record_json["Intensity_Jul"] = 0
            record_json["Intensity_Aug"] = 0
            record_json["Intensity_Sep"] = 0
            record_json["Intensity_Oct"] = 0
            record_json["Intensity_Nov"] = 0
            record_json["Intensity_Dec"] = 0
            record_json["Intensity_Jan"] = 0
            record_json["Intensity_Feb"] = 0
            record_json["Intensity_Mar"] = 0
            record_json["Total_Intensity"] = 0     
            result.append(record_json)   

    try:
        intensity_years = Scope3_Emissions_by_Facilities.objects.values_list('Financial_Year', flat=True).distinct()
        turnover_years = Turnover.objects.values_list('Financial_Year', flat=True)
        elements_in_list2_not_in_list1 = list(set(turnover_years) - set(intensity_years))
        for elem in elements_in_list2_not_in_list1:
            record_json = {}
            record_json["Financial_Year"] = elem
            record_json["Facility"] = "NA"
            record_json["Intensity_Apr"] = 0
            record_json["Intensity_May"] = 0
            record_json["Intensity_Jun"] = 0
            record_json["Intensity_Jul"] = 0
            record_json["Intensity_Aug"] = 0
            record_json["Intensity_Sep"] = 0
            record_json["Intensity_Oct"] = 0
            record_json["Intensity_Nov"] = 0
            record_json["Intensity_Dec"] = 0
            record_json["Intensity_Jan"] = 0
            record_json["Intensity_Feb"] = 0
            record_json["Intensity_Mar"] = 0
            record_json["Total_Intensity"] = 0
            result.append(record_json)
    except Exception as e:
        print(f"An error occurred: {e}")

    return result    

###########################################    Waste     ##########################################################

def calculate_waste_intensity():
    from .models import Waste_Generated
    from CompanyDetails.models import Turnover
    all_objects = Waste_Generated.objects.all()
    result = []
    for obj in all_objects:
        record_json = {}
        record_json["Financial_Year"] = obj.Financial_Year
        record_json["Facility"] = obj.Facility
        try:
            turnover = Turnover.objects.get(Financial_Year=record_json["Financial_Year"])
            turnover_values = [
                Decimal(turnover.Turnover_Apr.to_decimal()), Decimal(turnover.Turnover_May.to_decimal()),
                Decimal(turnover.Turnover_Jun.to_decimal()), Decimal(turnover.Turnover_Jul.to_decimal()),
                Decimal(turnover.Turnover_Aug.to_decimal()), Decimal(turnover.Turnover_Sep.to_decimal()),
                Decimal(turnover.Turnover_Oct.to_decimal()), Decimal(turnover.Turnover_Nov.to_decimal()),
                Decimal(turnover.Turnover_Dec.to_decimal()), Decimal(turnover.Turnover_Jan.to_decimal()),
                Decimal(turnover.Turnover_Feb.to_decimal()), Decimal(turnover.Turnover_Mar.to_decimal())
            ]
            
            generated_values = [
                Decimal(obj.Waste_Generated_Apr.to_decimal()), Decimal(obj.Waste_Generated_May.to_decimal()),
                Decimal(obj.Waste_Generated_Jun.to_decimal()), Decimal(obj.Waste_Generated_Jul.to_decimal()),
                Decimal(obj.Waste_Generated_Aug.to_decimal()), Decimal(obj.Waste_Generated_Sep.to_decimal()),
                Decimal(obj.Waste_Generated_Oct.to_decimal()), Decimal(obj.Waste_Generated_Nov.to_decimal()),
                Decimal(obj.Waste_Generated_Dec.to_decimal()), Decimal(obj.Waste_Generated_Jan.to_decimal()),
                Decimal(obj.Waste_Generated_Feb.to_decimal()), Decimal(obj.Waste_Generated_Mar.to_decimal())
            ]
            
            waste_intensity = []
            for i in range(12):
                try:
                    # Calculate waste intensity only if turnover is not zero
                    if turnover_values[i] > 0:
                        waste_intensity.append(round(float(generated_values[i] / turnover_values[i]), 2))
                    else:
                        waste_intensity.append(0)  # Or any default value you prefer
                except DivisionByZero:
                    waste_intensity.append(0)  # Default value in case of division by zero

            # Assign waste intensity values to each month
            months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
            for i, month in enumerate(months):
                record_json[f"Waste_Intensity_{month}"] = waste_intensity[i]

            # Calculate total waste intensity
            record_json["Total_Waste_Intensity"] = round(sum(waste_intensity), 2)
            
            result.append(record_json)

        except Turnover.DoesNotExist:
            # Handle the case where Turnover data for the financial year doesn't exist
            print(f"Turnover data missing for Financial Year: {record_json['Financial_Year']}")


        except Turnover.DoesNotExist:
            record_json["Waste_Intensity_Apr"] = 0
            record_json["Waste_Intensity_May"] = 0
            record_json["Waste_Intensity_Jun"] = 0
            record_json["Waste_Intensity_Jul"] = 0
            record_json["Waste_Intensity_Aug"] = 0
            record_json["Waste_Intensity_Sep"] = 0
            record_json["Waste_Intensity_Oct"] = 0
            record_json["Waste_Intensity_Nov"] = 0
            record_json["Waste_Intensity_Dec"] = 0
            record_json["Waste_Intensity_Jan"] = 0
            record_json["Waste_Intensity_Feb"] = 0
            record_json["Waste_Intensity_Mar"] = 0
            record_json["Total_Waste_Intensity"] = 0     
            result.append(record_json)   

    try:
        intensity_years = Waste_Generated.objects.values_list('Financial_Year', flat=True).distinct()
        turnover_years = Turnover.objects.values_list('Financial_Year', flat=True)
        elements_in_list2_not_in_list1 = list(set(turnover_years) - set(intensity_years))
        for elem in elements_in_list2_not_in_list1:
            record_json = {}
            record_json["Financial_Year"] = elem
            record_json["Facility"] = "NA"
            record_json["Waste_Intensity_Apr"] = 0
            record_json["Waste_Intensity_May"] = 0
            record_json["Waste_Intensity_Jun"] = 0
            record_json["Waste_Intensity_Jul"] = 0
            record_json["Waste_Intensity_Aug"] = 0
            record_json["Waste_Intensity_Sep"] = 0
            record_json["Waste_Intensity_Oct"] = 0
            record_json["Waste_Intensity_Nov"] = 0
            record_json["Waste_Intensity_Dec"] = 0
            record_json["Waste_Intensity_Jan"] = 0
            record_json["Waste_Intensity_Feb"] = 0
            record_json["Waste_Intensity_Mar"] = 0
            record_json["Total_Waste_Intensity"] = 0
            result.append(record_json)
    except Exception as e:
        print(f"An error occurred: {e}")

    return result







def calculate_water_intensity():
    result = []
    from .models import Water_Consumption
    from CompanyDetails.models import Turnover
    all_objects = Water_Consumption.objects.all()
    for obj in all_objects:
        record_json = {}
        record_json["Financial_Year"] = obj.Financial_Year
        record_json["Facility"] = obj.Facility
        try:
            turnover = Turnover.objects.get(Financial_Year=record_json["Financial_Year"])
            turnover_apr = Decimal(turnover.Turnover_Apr.to_decimal())
            turnover_may = Decimal(turnover.Turnover_May.to_decimal())
            turnover_jun = Decimal(turnover.Turnover_Jun.to_decimal())
            turnover_jul = Decimal(turnover.Turnover_Jul.to_decimal())
            turnover_aug = Decimal(turnover.Turnover_Aug.to_decimal())
            turnover_sep = Decimal(turnover.Turnover_Sep.to_decimal())
            turnover_oct = Decimal(turnover.Turnover_Oct.to_decimal())
            turnover_nov = Decimal(turnover.Turnover_Nov.to_decimal())
            turnover_dec = Decimal(turnover.Turnover_Dec.to_decimal())
            turnover_jan = Decimal(turnover.Turnover_Jan.to_decimal())
            turnover_feb = Decimal(turnover.Turnover_Feb.to_decimal())
            turnover_mar = Decimal(turnover.Turnover_Mar.to_decimal())
            
            consumption_apr = Decimal(obj.Water_Consumption_Apr.to_decimal())
            consumption_may = Decimal(obj.Water_Consumption_May.to_decimal())
            consumption_jun = Decimal(obj.Water_Consumption_Jun.to_decimal())
            consumption_jul = Decimal(obj.Water_Consumption_Jul.to_decimal())
            consumption_aug = Decimal(obj.Water_Consumption_Aug.to_decimal())
            consumption_sep = Decimal(obj.Water_Consumption_Sep.to_decimal())
            consumption_oct = Decimal(obj.Water_Consumption_Oct.to_decimal())
            consumption_nov = Decimal(obj.Water_Consumption_Nov.to_decimal())
            consumption_dec = Decimal(obj.Water_Consumption_Dec.to_decimal())
            consumption_jan = Decimal(obj.Water_Consumption_Jan.to_decimal())
            consumption_feb = Decimal(obj.Water_Consumption_Feb.to_decimal())
            consumption_mar = Decimal(obj.Water_Consumption_Mar.to_decimal())

            record_json["Water_Intensity_Apr"] = round(float(consumption_apr / turnover_apr), 2) if turnover_apr > 0 else 0
            record_json["Water_Intensity_May"] = round(float(consumption_may / turnover_may), 2) if turnover_may > 0 else 0
            record_json["Water_Intensity_Jun"] = round(float(consumption_jun / turnover_jun), 2) if turnover_jun > 0 else 0
            record_json["Water_Intensity_Jul"] = round(float(consumption_jul / turnover_jul), 2) if turnover_jul > 0 else 0
            record_json["Water_Intensity_Aug"] = round(float(consumption_aug / turnover_aug), 2) if turnover_aug > 0 else 0
            record_json["Water_Intensity_Sep"] = round(float(consumption_sep / turnover_sep), 2) if turnover_sep > 0 else 0
            record_json["Water_Intensity_Oct"] = round(float(consumption_oct / turnover_oct), 2) if turnover_oct > 0 else 0
            record_json["Water_Intensity_Nov"] = round(float(consumption_nov / turnover_nov), 2) if turnover_nov > 0 else 0
            record_json["Water_Intensity_Dec"] = round(float(consumption_dec / turnover_dec), 2) if turnover_dec > 0 else 0
            record_json["Water_Intensity_Jan"] = round(float(consumption_jan / turnover_jan), 2) if turnover_jan > 0 else 0
            record_json["Water_Intensity_Feb"] = round(float(consumption_feb / turnover_feb), 2) if turnover_feb > 0 else 0
            record_json["Water_Intensity_Mar"] = round(float(consumption_mar / turnover_mar), 2) if turnover_mar > 0 else 0
            record_json["Total_Water_Intensity"] = round(record_json["Water_Intensity_Apr"] + record_json["Water_Intensity_May"] + record_json["Water_Intensity_Jun"] + record_json["Water_Intensity_Jul"] + record_json["Water_Intensity_Aug"] + record_json["Water_Intensity_Sep"] + record_json["Water_Intensity_Oct"] + record_json["Water_Intensity_Nov"] + record_json["Water_Intensity_Dec"] + record_json["Water_Intensity_Jan"] + record_json["Water_Intensity_Feb"] + record_json["Water_Intensity_Mar"], 2)

            result.append(record_json)

        except Turnover.DoesNotExist:
            record_json["Water_Intensity_Apr"] = 0
            record_json["Water_Intensity_May"] = 0
            record_json["Water_Intensity_Jun"] = 0
            record_json["Water_Intensity_Jul"] = 0
            record_json["Water_Intensity_Aug"] = 0
            record_json["Water_Intensity_Sep"] = 0
            record_json["Water_Intensity_Oct"] = 0
            record_json["Water_Intensity_Nov"] = 0
            record_json["Water_Intensity_Dec"] = 0
            record_json["Water_Intensity_Jan"] = 0
            record_json["Water_Intensity_Feb"] = 0
            record_json["Water_Intensity_Mar"] = 0
            record_json["Total_Water_Intensity"] = 0     
            result.append(record_json)   

    try:
        intensity_years = Water_Consumption.objects.values_list('Financial_Year', flat=True).distinct()
        turnover_years = Turnover.objects.values_list('Financial_Year', flat=True)
        elements_in_list2_not_in_list1 = list(set(turnover_years) - set(intensity_years))
        for elem in elements_in_list2_not_in_list1:
            record_json = {}
            record_json["Financial_Year"] = elem
            record_json["Facility"] = "NA"
            record_json["Water_Intensity_Apr"] = 0
            record_json["Water_Intensity_May"] = 0
            record_json["Water_Intensity_Jun"] = 0
            record_json["Water_Intensity_Jul"] = 0
            record_json["Water_Intensity_Aug"] = 0
            record_json["Water_Intensity_Sep"] = 0
            record_json["Water_Intensity_Oct"] = 0
            record_json["Water_Intensity_Nov"] = 0
            record_json["Water_Intensity_Dec"] = 0
            record_json["Water_Intensity_Jan"] = 0
            record_json["Water_Intensity_Feb"] = 0
            record_json["Water_Intensity_Mar"] = 0
            record_json["Total_Water_Intensity"] = 0
            result.append(record_json)
    except Exception as e:
        print(f"An error occurred: {e}")

    return result