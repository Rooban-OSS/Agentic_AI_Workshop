import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def generate_delivery_data_template():
    """Generate comprehensive delivery data template with Indian context"""
    
    # Sample data with Indian cities and realistic values
    delivery_template = pd.DataFrame({
        # Core required fields
        'date': [
            '2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19',
            '2024-01-20', '2024-01-22', '2024-01-23', '2024-01-24', '2024-01-25'
        ],
        'route_id': [
            'MUM_001', 'DEL_002', 'BLR_003', 'MUM_001', 'CHE_004',
            'HYD_005', 'DEL_002', 'KOL_006', 'PUN_007', 'MUM_001'
        ],
        'delivery_time_hours': [
            4.5, 6.2, 3.8, 5.1, 7.3, 4.9, 5.8, 6.5, 4.2, 3.9
        ],
        'distance_km': [
            120, 180, 95, 135, 220, 145, 165, 198, 110, 88
        ],
        'fuel_cost_inr': [
            1200, 1800, 950, 1350, 2200, 1450, 1650, 1980, 1100, 880
        ],
        'packages_delivered': [
            25, 18, 32, 28, 15, 30, 22, 19, 35, 40
        ],
        'on_time_delivery': [
            True, False, True, True, False, True, True, False, True, True
        ],
        
        # Additional contextual fields for better analysis
        'driver_id': [
            'DRV001', 'DRV002', 'DRV003', 'DRV001', 'DRV004',
            'DRV005', 'DRV002', 'DRV006', 'DRV007', 'DRV001'
        ],
        'vehicle_type': [
            'Truck_Large', 'Van_Medium', 'Truck_Small', 'Truck_Large', 'Truck_Medium',
            'Van_Large', 'Van_Medium', 'Truck_Large', 'Van_Small', 'Truck_Small'
        ],
        'start_city': [
            'Mumbai', 'Delhi', 'Bangalore', 'Mumbai', 'Chennai',
            'Hyderabad', 'Delhi', 'Kolkata', 'Pune', 'Mumbai'
        ],
        'end_city': [
            'Pune', 'Gurgaon', 'Mysore', 'Nashik', 'Pondicherry',
            'Warangal', 'Noida', 'Durgapur', 'Satara', 'Thane'
        ],
        'weather_condition': [
            'Clear', 'Rain', 'Clear', 'Fog', 'Heavy_Rain',
            'Clear', 'Smog', 'Rain', 'Clear', 'Clear'
        ],
        'traffic_condition': [
            'Normal', 'Heavy', 'Light', 'Normal', 'Heavy',
            'Normal', 'Heavy', 'Normal', 'Light', 'Light'
        ],
        'fuel_price_per_liter': [
            105.50, 108.20, 104.80, 105.50, 107.90,
            106.30, 108.20, 103.60, 105.20, 105.50
        ],
        'toll_charges_inr': [
            150, 280, 80, 120, 350, 200, 250, 320, 100, 60
        ],
        'driver_overtime_hours': [
            0, 2.2, 0, 1.1, 3.3, 0.9, 1.8, 2.5, 0, 0
        ],
        'maintenance_cost_inr': [
            200, 450, 150, 250, 600, 300, 400, 500, 180, 120
        ],
        'delivery_priority': [
            'Standard', 'Express', 'Standard', 'Standard', 'Express',
            'Standard', 'Standard', 'Express', 'Standard', 'Standard'
        ]
    })
    
    return delivery_template

def generate_inventory_data_template():
    """Generate comprehensive inventory data template with Indian context"""
    
    # Sample data with Indian suppliers and realistic INR values
    inventory_template = pd.DataFrame({
        # Core required fields  
        'product_id': [
            'PROD_001', 'PROD_002', 'PROD_003', 'PROD_004', 'PROD_005',
            'PROD_006', 'PROD_007', 'PROD_008', 'PROD_009', 'PROD_010'
        ],
        'current_stock': [
            150, 45, 280, 75, 320, 90, 180, 60, 240, 110
        ],
        'reorder_point': [
            100, 50, 200, 80, 250, 100, 150, 70, 180, 120
        ],
        'holding_cost_per_unit_inr': [
            12.50, 25.75, 8.25, 45.00, 15.60, 35.25, 18.80, 55.40, 22.30, 28.90
        ],
        'demand_last_30_days': [
            85, 62, 120, 45, 180, 55, 95, 40, 110, 70
        ],
        'supplier_lead_time_days': [
            7, 14, 5, 21, 10, 18, 12, 25, 8, 15
        ],
        
        # Additional contextual fields for comprehensive analysis
        'product_name': [
            'Electronics_Component_A', 'Textile_Material_B', 'Home_Appliance_C',
            'Automotive_Part_D', 'Food_Product_E', 'Pharmaceutical_F',
            'Cosmetic_Item_G', 'Industrial_Tool_H', 'Sports_Equipment_I', 'Book_J'
        ],
        'product_category': [
            'Electronics', 'Textiles', 'Home_Appliances', 'Automotive', 'Food_FMCG',
            'Pharmaceuticals', 'Beauty_Personal_Care', 'Industrial', 'Sports_Recreation', 'Books_Stationery'
        ],
        'supplier_name': [
            'Mumbai_Electronics_Ltd', 'Gujarat_Textiles_Pvt', 'Karnataka_Appliances_Corp',
            'Tamil_Nadu_Auto_Parts', 'Delhi_Foods_Ltd', 'Hyderabad_Pharma_Inc',
            'Pune_Cosmetics_Co', 'Rajasthan_Tools_Ltd', 'Kerala_Sports_Mfg', 'Bengal_Books_House'
        ],
        'supplier_city': [
            'Mumbai', 'Ahmedabad', 'Bangalore', 'Chennai', 'Delhi',
            'Hyderabad', 'Pune', 'Jaipur', 'Kochi', 'Kolkata'
        ],
        'warehouse_location': [
            'Mumbai_WH_01', 'Delhi_WH_02', 'Bangalore_WH_03', 'Chennai_WH_01', 'Delhi_WH_01',
            'Hyderabad_WH_01', 'Pune_WH_01', 'Mumbai_WH_02', 'Kochi_WH_01', 'Kolkata_WH_01'
        ],
        'unit_purchase_cost_inr': [
            450.00, 125.50, 2800.75, 1250.25, 85.60,
            750.80, 320.45, 1850.90, 560.30, 245.70
        ],
        'unit_selling_price_inr': [
            675.00, 188.25, 4201.13, 1875.38, 128.40,
            1126.20, 480.68, 2776.35, 840.45, 368.55
        ],
        'storage_temperature_req': [
            'Room_Temp', 'Room_Temp', 'Room_Temp', 'Room_Temp', 'Cold_Storage',
            'Climate_Controlled', 'Room_Temp', 'Room_Temp', 'Room_Temp', 'Room_Temp'
        ],
        'shelf_life_days': [
            365, 730, 1095, 1825, 90, 180, 540, 1460, 1095, 3650
        ],
        'seasonal_demand_factor': [
            1.0, 1.2, 0.8, 1.1, 1.5, 1.0, 1.3, 0.9, 1.4, 1.1
        ],
        'abc_classification': [
            'A', 'B', 'A', 'C', 'A', 'B', 'B', 'C', 'A', 'B'
        ],
        'supplier_rating': [
            4.2, 3.8, 4.5, 3.5, 4.0, 4.3, 3.9, 3.6, 4.1, 4.4
        ],
        'minimum_order_quantity': [
            50, 100, 25, 200, 500, 100, 150, 50, 75, 300
        ]
    })
    
    return inventory_template

def create_data_documentation():
    """Create comprehensive documentation for the data templates"""
    
    documentation = """
# LOGISTICS DATA TEMPLATES - FIELD DESCRIPTIONS

## OVERVIEW
These templates (`delivery_data_template.csv` and `inventory_data_template.csv`) are designed for use with the **Logistics Optimization Crew AI System** Streamlit app. Fill these templates with your actual logistics data and upload them to the app via the sidebar to perform optimization analysis. Ensure all **required fields** are included to pass validation. **Optional fields** are not mandatory but can enhance the quality of the analysis.

## DELIVERY DATA TEMPLATE (delivery_data_template.csv)

### REQUIRED FIELDS (Must be present for analysis):
- **date**: Delivery date in YYYY-MM-DD format (e.g., 2024-01-15)
- **route_id**: Unique identifier for delivery route (e.g., MUM_001, DEL_002)
- **delivery_time_hours**: Total time taken for delivery in hours (decimal, e.g., 4.5)
- **distance_km**: Total distance covered in kilometers (e.g., 120)
- **fuel_cost_inr**: Total fuel cost in Indian Rupees (₹, e.g., 1200)
- **packages_delivered**: Number of packages delivered (integer, e.g., 25)
- **on_time_delivery**: Boolean (True/False) indicating if delivery was on time

### OPTIONAL FIELDS (Enhance analysis quality):
- **driver_id**: Unique identifier for driver (e.g., DRV001)
- **vehicle_type**: Type of vehicle used (e.g., Truck_Large, Van_Medium)
- **start_city**: Starting city/location (e.g., Mumbai)
- **end_city**: Destination city/location (e.g., Pune)
- **weather_condition**: Weather during delivery (e.g., Clear, Rain, Fog)
- **traffic_condition**: Traffic conditions (e.g., Light, Normal, Heavy)
- **fuel_price_per_liter**: Fuel price in ₹ per liter (e.g., 105.50)
- **toll_charges_inr**: Total toll charges in ₹ (e.g., 150)
- **driver_overtime_hours**: Overtime hours for driver (e.g., 2.2)
- **maintenance_cost_inr**: Vehicle maintenance cost in ₹ (e.g., 200)
- **delivery_priority**: Priority level (e.g., Standard, Express)

## INVENTORY DATA TEMPLATE (inventory_data_template.csv)

### REQUIRED FIELDS (Must be present for analysis):
- **product_id**: Unique identifier for product (e.g., PROD_001)
- **current_stock**: Current inventory level in units (e.g., 150)
- **reorder_point**: Minimum stock level before reordering (e.g., 100)
- **holding_cost_per_unit_inr**: Cost to hold one unit in inventory in ₹ (e.g., 12.50)
- **demand_last_30_days**: Demand quantity in last 30 days (e.g., 85)
- **supplier_lead_time_days**: Time taken by supplier to deliver in days (e.g., 7)

### OPTIONAL FIELDS (Enhance analysis quality):
- **product_name**: Descriptive name of the product (e.g., Electronics_Component_A)
- **product_category**: Category classification (e.g., Electronics)
- **supplier_name**: Name of the supplier company (e.g., Mumbai_Electronics_Ltd)
- **supplier_city**: Supplier's city location (e.g., Mumbai)
- **warehouse_location**: Storage warehouse identifier (e.g., Mumbai_WH_01)
- **unit_purchase_cost_inr**: Cost to purchase one unit in ₹ (e.g., 450.00)
- **unit_selling_price_inr**: Selling price per unit in ₹ (e.g., 675.00)
- **storage_temperature_req**: Storage requirements (e.g., Room_Temp, Cold_Storage)
- **shelf_life_days**: Product shelf life in days (e.g., 365)
- **seasonal_demand_factor**: Multiplier for seasonal demand variations (e.g., 1.0)
- **abc_classification**: ABC analysis classification (e.g., A, B, C)
- **supplier_rating**: Supplier performance rating (1-5, e.g., 4.2)
- **minimum_order_quantity**: Minimum order quantity from supplier (e.g., 50)

## DATA QUALITY GUIDELINES:

### Date Formats:
- Use YYYY-MM-DD format (e.g., 2024-01-15)
- Ensure dates are valid and within a reasonable range (e.g., not in the future)

### Numerical Fields:
- Use decimal points for fractional values (e.g., 4.5 hours, 12.50 ₹)
- Do not include currency symbols in numerical fields (use raw numbers)
- Negative values are not allowed for costs, distances, or quantities
- Ensure realistic ranges (e.g., fuel_cost_inr should reflect Indian fuel prices)

### Text Fields:
- Use consistent naming conventions (e.g., MUM_001 for route_id)
- Avoid special characters that might cause parsing issues (e.g., commas, quotes)
- Use underscores instead of spaces in categorical values (e.g., Truck_Large)

### Boolean Fields:
- Use True/False (case-sensitive) or 1/0 for true/false respectively

## INDIAN MARKET SPECIFIC CONSIDERATIONS:

### Route Planning:
- Account for monsoon seasons (June-September) affecting delivery times
- Consider festival periods (e.g., Diwali, Durga Puja) causing traffic/delays
- Include tier-1, tier-2, tier-3 city classifications for accurate routing

### Cost Factors:
- Fuel prices vary by state due to different taxes (e.g., ~₹100-110/liter)
- Toll charges are significant for highway routes (e.g., ₹50-500 per route)
- Labor costs vary across regions (e.g., higher in metro cities)

### Seasonal Patterns:
- Festival seasons: Diwali (Oct-Nov), Durga Puja (Sep-Oct), Christmas (Dec)
- Wedding seasons: November-February, April-May
- Monsoon impacts: June-September logistics challenges

### Regional Variations:
- North India: Heavy traffic in Delhi-NCR, winter fog delays
- South India: Strong port access, better road infrastructure
- East/West: Unique supplier networks and logistics challenges

## SAMPLE SIZE RECOMMENDATIONS:
- **Minimum**: 100 delivery records, 50 inventory items
- **Good**: 500+ delivery records, 100+ inventory items
- **Optimal**: 1000+ delivery records, 200+ inventory items

## COMMON DATA ERRORS TO AVOID:
- Missing or invalid dates (e.g., 2024-13-01)
- Negative costs, distances, or quantities
- Inconsistent naming (e.g., MUM_001 vs Mumbai_001)
- Missing required fields
- Extreme outliers (e.g., fuel_cost_inr of ₹1,000,000)

## HOW TO USE WITH THE STREAMLIT APP:
1. Open the generated template files (`delivery_data_template.csv`, `inventory_data_template.csv`) in a spreadsheet editor (e.g., Excel, Google Sheets).
2. Replace the sample data with your actual logistics data, ensuring all **required fields** are filled.
3. Save the files as CSV (Comma-Separated Values) format.
4. Run the **Logistics Optimization Crew AI System** Streamlit app (`streamlit run logistics_optimization_crew.py`).
5. In the app's sidebar, upload the filled `delivery_data_template.csv` and `inventory_data_template.csv` files.
6. Ensure the data passes validation (all required columns must be present: date, route_id, delivery_time_hours, distance_km, fuel_cost_inr, packages_delivered, on_time_delivery for delivery data; product_id, current_stock, reorder_point, holding_cost_per_unit_inr, demand_last_30_days, supplier_lead_time_days for inventory data).
7. Click "Start Analysis" to generate optimization insights based on your data.

Fill the templates with your actual data following these guidelines for optimal results in the Logistics Optimization Crew AI System.
"""
    
    return documentation

def main():
    """Generate all template files"""
    
    print("Generating Logistics Data Templates for Logistics Optimization Crew AI System...")
    
    # Generate templates
    delivery_template = generate_delivery_data_template()
    inventory_template = generate_inventory_data_template()
    documentation = create_data_documentation()
    
    # Save templates
    delivery_template.to_csv('delivery_data_template.csv', index=False)
    inventory_template.to_csv('inventory_data_template.csv', index=False)
    
    # Save documentation
    with open('DATA_TEMPLATE_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(documentation)
    
    print("✅ Templates generated successfully!")
    print("\nFiles created:")
    print("📊 delivery_data_template.csv - Template for delivery data")
    print("📦 inventory_data_template.csv - Template for inventory data")
    print("📋 DATA_TEMPLATE_GUIDE.md - Comprehensive field documentation")
    print("\nInstructions:")
    print("1. Open the CSV templates in a spreadsheet editor (e.g., Excel, Google Sheets).")
    print("2. Replace the sample data with your actual logistics data, ensuring all required fields are included.")
    print("3. Required delivery data columns: date, route_id, delivery_time_hours, distance_km, fuel_cost_inr, packages_delivered, on_time_delivery")
    print("4. Required inventory data columns: product_id, current_stock, reorder_point, holding_cost_per_unit_inr, demand_last_30_days, supplier_lead_time_days")
    print("5. Save the files as CSV format.")
    print("6. Upload the filled templates to the Logistics Optimization Crew AI System Streamlit app via the sidebar.")
    print("7. Run the analysis to get optimization insights.")

if __name__ == "__main__":
    main()