from decimal import Decimal
from bson.decimal128 import Decimal128



# Step 3: Function to safely convert database values to floats
def safe_decimal(value):
    if value is None:
        return 0.0
    if isinstance(value, Decimal128):
        return float(value.to_decimal())
    if isinstance(value, Decimal):
        return float(value)
    return float(str(value))

# Step 4: Calculate ratio (turnover / networth)
def ratio(turnover, networth):
    net = safe_decimal(networth)
    turn = safe_decimal(turnover)
    return round(turn / net, 2) if net != 0 else 0.0

# Step 5: Calculate change and percent change between consecutive quarters
def get_change(prev, curr):
    change = round(curr - prev, 2)
    percent = round((change / prev) * 100, 2) if prev != 0 else 0.0
    return {"change": change, "percent": percent}