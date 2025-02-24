from datetime import datetime

def generate_financial_years(start_year):
    current_year = datetime.now().year
    financial_years = []
    
    # Generate financial years up to the previous year
    for year in range(start_year, current_year):
        next_year = year + 1
        financial_year = f"FY{year}-{next_year}"
        financial_years.append(financial_year)

    # Add the current financial year
    next_year = current_year + 1
    current_financial_year = f"FY{current_year}-{next_year}"
    financial_years.append(current_financial_year)
    
    financial_years.reverse()

    return financial_years
