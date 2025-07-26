
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
