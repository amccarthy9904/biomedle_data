import ee

# Authenticate with your Earth Engine account
ee.Initialize()

# Load the countries dataset
countries = ee.FeatureCollection('FAO/GAUL/2015/level0')

# Get a list of all country names
country_names = list(set(countries.aggregate_array('ADM0_NAME').getInfo()))

i = 0
# Print the names of every country
for country_name in country_names:
    i += 1
    print(f' {i} {country_name}')

