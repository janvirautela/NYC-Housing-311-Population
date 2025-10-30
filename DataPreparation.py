#Import key libraries
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

conn = psycopg2.connect(
    dbname="nyc_housing_analysis",
    user="postgres",
    password="Siddu@1903",
    host="localhost",
    port="5432"
)
try:
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("Connected successfully to:", cur.fetchone())
except Exception as e:
    print("Connection failed:", e)


#Load all three tables
violations_df = pd.read_sql("SELECT * FROM housing_violations;", conn)
requests_df = pd.read_sql("SELECT * FROM service_requests_311;", conn)
population_df = pd.read_sql("SELECT * FROM population_forecast;", conn)

#Display first few rows of each
print("Housing Violations:")
display(violations_df.head())
print("\nService Requests:")
display(requests_df.head())
print("\nPopulation Forecast:")
display(population_df.head())

print("Missing Values in Housing Violations:")
print(violations_df.isnull().sum(), "\n")

print("Missing Values in Service Requests:")
print(requests_df.isnull().sum(), "\n")

print("Missing Values in Population Forecast:")
print(population_df.isnull().sum())

#Housing Violations
print("Housing Violations Shape:", violations_df.shape)

#Service Requests
print("Service Requests Shape:", requests_df.shape)

#Population Forecast
print("Population Forecast Shape:", population_df.shape)

violations_df.dropna(subset=["postcode"], inplace=True)
requests_df.dropna(subset=["incident_zip", "latitude", "longitude", "resolution"], inplace=True)


print("After Dropping Missing Values:")
print("Housing Violations:", violations_df.shape)
print("Service Requests:", requests_df.shape)

print("Housing Violations — Info:")
print("\n Housing Violations — Summary Stats:")
print(violations_df.describe(include='all'))

print("\nService Requests — Info:")
requests_df.info()
print("\nService Requests — Summary Stats:")
print(requests_df.describe(include='all'))

print("\n Population Forecast — Info:")
population_df.info()
print("\n Population Forecast — Summary Stats:")
print(population_df.describe(include='all'))

#Check if there are any duplicate rows
duplicates_housing = violations_df.duplicated().sum()
print(f"Housing Violations — Total duplicate rows: {duplicates_housing}")
#View the first few duplicates
if duplicates_housing > 0:
    print(violations_df[violations_df.duplicated()].head())

duplicates_service = requests_df.duplicated().sum()
print(f"Service Requests — Total duplicate rows: {duplicates_service}")
if duplicates_service > 0:
    print(requests_df[requests_df.duplicated()].head())
#Remove duplicates if found
requests_df.drop_duplicates(inplace=True)
print(f"After removing duplicates: {requests_df.shape}")

duplicates_population = population_df.duplicated().sum()
print(f"Population Forecast — Total duplicate rows: {duplicates_population}")
if duplicates_population > 0:
    print(population_df[population_df.duplicated()].head())
#Remove duplicates if needed
population_df.drop_duplicates(inplace=True)
print(f"After removing duplicates: {population_df.shape}")

print("Before conversion:")
print(violations_df.dtypes)
#Convert inspection_date → datetime
violations_df['inspection_date'] = pd.to_datetime(
    violations_df['inspection_date'], errors='coerce', format='%d-%m-%Y'
)
#Convert postcode → string (some ZIPs may look numeric)
violations_df['postcode'] = violations_df['postcode'].astype(str)
print("\nAfter conversion:")
print(violations_df.dtypes)

print("\nBefore conversion:")
print(requests_df.dtypes)
#Convert created_date → datetime
requests_df['created_date'] = pd.to_datetime(
    requests_df['created_date'], errors='coerce', format='%d-%m-%Y %H:%M'
)
#Ensure ZIP code is text, not number
requests_df['incident_zip'] = requests_df['incident_zip'].astype(str)
print("\nAfter conversion:")
print(requests_df.dtypes)

print("\nBefore conversion:")
print(population_df.dtypes)
# Make sure population columns are integers
population_df[['population_2020', 'population_2030', 'population_2040']] = \
population_df[['population_2020', 'population_2030', 'population_2040']].astype(int)
print("\nAfter conversion:")
print(population_df.dtypes)

#Check date range
print(violations_df['inspection_date'].min(), violations_df['inspection_date'].max())
#Filter if any wrong years appear (e.g., before 2010 or after 2025)
violations_df = violations_df[
    (violations_df['inspection_date'] >= '2010-01-01') &
    (violations_df['inspection_date'] <= '2025-12-31')
]

#NYC roughly ranges between:
#Latitude: 40.4 – 41.0, Longitude: -74.3 – -73.6
invalid_coords = requests_df[
    (requests_df['latitude'] < 40.4) | (requests_df['latitude'] > 41.0) |
    (requests_df['longitude'] < -74.3) | (requests_df['longitude'] > -73.6)
]
print(f"Invalid coordinate rows: {len(invalid_coords)}")
#Drop them
requests_df = requests_df.drop(invalid_coords.index)
print(f"After removing invalid coordinates: {requests_df.shape}")

print(population_df.describe())
#Sanity check
outliers_pop = population_df[
    (population_df['population_2020'] < 500000) | (population_df['population_2020'] > 10000000)
]
print(outliers_pop)
