import ee
import os
import requests
import subprocess

# list of names from react library
country_names = ['Andorra', 'United Arab Emirates', 'Afghanistan', 'Antigua and Barbuda', 'Anguilla', 'Albania', 'Armenia', 'Angola', 'Antarctica', 'Argentina', 'American Samoa', 'Austria', 'Australia', 'Aruba', 'Åland Islands', 'Azerbaijan', 'Bosnia and Herzegovina', 'Barbados', 'Bangladesh', 'Belgium', 'Burkina Faso', 'Bulgaria', 'Bahrain', 'Burundi', 'Benin', 'Saint Barthélemy', 'Bermuda', 'Brunei Darussalam', 'Bolivia, Plurinational State of', 'Bonaire, Sint Eustatius and Saba', 'Brazil', 'Bahamas', 'Bhutan', 'Bouvet Island', 'Botswana', 'Belarus', 'Belize', 'Canada', 'Cocos (Keeling) Islands', 'Congo, Democratic Republic of the', 'Central African Republic', 'Congo', 'Switzerland', 'Côte d\'Ivoire', 'Cook Islands', 'Chile', 'Cameroon', 'China', 'Colombia', 'Costa Rica', 'Cuba', 'Cabo Verde', 'Curaçao', 'Christmas Island', 'Cyprus', 'Czechia', 'Germany', 'Djibouti', 'Denmark', 'Dominica', 'Dominican Republic', 'Algeria', 'Ecuador', 'Estonia', 'Egypt', 'Western Sahara', 'Eritrea', 'Spain', 'Ethiopia', 'Finland', 'Fiji', 'Falkland Islands (Malvinas)', 'Micronesia, Federated States of', 'Faroe Islands', 'France', 'Gabon', 'United Kingdom of Great Britain and Northern Ireland', 'Grenada', 'Georgia', 'French Guiana', 'Guernsey', 'Ghana', 'Gibraltar', 'Greenland', 'Gambia', 'Guinea', 'Guadeloupe', 'Equatorial Guinea', 'Greece', 'South Georgia and the South Sandwich Islands', 'Guatemala', 'Guam', 'Guinea-Bissau', 'Guyana', 'Hong Kong', 'Heard Island and McDonald Islands', 'Honduras', 'Croatia', 'Haiti', 'Hungary', 'Indonesia', 'Ireland', 'Israel', 'Isle of Man', 'India', 'British Indian Ocean Territory', 'Iraq', 'Iran, Islamic Republic of', 'Iceland', 'Italy', 'Jersey', 'Jamaica', 'Jordan', 'Japan', 'Kenya', 'Kyrgyzstan', 'Cambodia', 'Kiribati', 'Comoros', 'Saint Kitts and Nevis', 'Korea, Democratic People\'s Republic of', 'Korea, Republic of', 'Kuwait', 'Cayman Islands', 'Kazakhstan', 'Lao People\'s Democratic Republic', 'Lebanon', 'Saint Lucia', 'Liechtenstein', 'Sri Lanka', 'Liberia', 'Lesotho', 'Lithuania', 'Luxembourg', 'Latvia', 'Libya', 'Morocco', 'Monaco', 'Moldova, Republic of', 'Montenegro', 'Saint Martin, (French part)', 'Madagascar', 'Marshall Islands', 'North Macedonia', 'Mali', 'Myanmar', 'Mongolia', 'Macao', 'Northern Mariana Islands', 'Martinique', 'Mauritania', 'Montserrat', 'Malta', 'Mauritius', 'Maldives', 'Malawi', 'Mexico', 'Malaysia', 'Mozambique', 'Namibia', 'New Caledonia', 'Niger', 'Norfolk Island', 'Nigeria', 'Nicaragua', 'Netherlands', 'Norway', 'Nepal', 'Nauru', 'Niue', 'New Zealand', 'Oman', 'Panama', 'Peru', 'French Polynesia', 'Papua New Guinea', 'Philippines', 'Pakistan', 'Poland', 'Saint Pierre and Miquelon', 'Pitcairn', 'Puerto Rico', 'Palestine, State of', 'Portugal', 'Palau', 'Paraguay', 'Qatar', 'Réunion', 'Romania', 'Serbia', 'Russian Federation', 'Rwanda', 'Saudi Arabia', 'Solomon Islands', 'Seychelles', 'Sudan', 'Sweden', 'Singapore', 'Saint Helena, Ascension and Tristan da Cunha', 'Slovenia', 'Svalbard and Jan Mayen', 'Slovakia', 'Sierra Leone', 'San Marino', 'Senegal', 'Somalia', 'Suriname', 'South Sudan', 'Sao Tome and Principe', 'El Salvador', 'Sint Maarten, (Dutch part)', 'Syrian Arab Republic', 'Eswatini', 'Turks and Caicos Islands', 'Chad', 'French Southern Territories', 'Togo', 'Thailand', 'Tajikistan', 'Tokelau', 'Timor-Leste', 'Turkmenistan', 'Tunisia', 'Tonga', 'Türkiye', 'Trinidad and Tobago', 'Tuvalu', 'Taiwan, Province of China', 'Tanzania, United Republic of', 'Ukraine', 'Uganda', 'United States Minor Outlying Islands', 'United States of America', 'Uruguay', 'Uzbekistan', 'Holy See', 'Saint Vincent and the Grenadines', 'Venezuela, Bolivarian Republic of', 'Virgin Islands, British', 'Virgin Islands, U.S.', 'Viet Nam', 'Vanuatu', 'Wallis and Futuna', 'Samoa', 'Yemen', 'Mayotte', 'South Africa', 'Zambia', 'Zimbabwe']
country_names = set(country_names)
# for i, name in enumerate(country_names):
#     print(f'{i} : {name}')

# Authenticate to the Earth Engine servers
ee.Initialize()

# Load the GAUL (Global Administrative Unit Layers) dataset
countries = ee.FeatureCollection('FAO/GAUL/2015/level0')
ecoRegions = ee.FeatureCollection('RESOLVE/ECOREGIONS/2017')

colorUpdates = [
    {'ECO_ID': 204, 'COLOR': '#B3493B'},
    {'ECO_ID': 245, 'COLOR': '#267400'},
    {'ECO_ID': 259, 'COLOR': '#004600'},
    {'ECO_ID': 286, 'COLOR': '#82F178'},
    {'ECO_ID': 316, 'COLOR': '#E600AA'},
    {'ECO_ID': 453, 'COLOR': '#5AA500'},
    {'ECO_ID': 317, 'COLOR': '#FDA87F'},
    {'ECO_ID': 763, 'COLOR': '#A93800'},
]

ecoRegions = ecoRegions.map(lambda f: f.set({'style': {'color': f.get('COLOR'), 'width': 0}}))

for update in colorUpdates:
    layer = ecoRegions.filterMetadata('ECO_ID', 'equals', update['ECO_ID']) \
        .map(lambda f: f.set({'style': {'color': update['COLOR'], 'width': 0}}))

    ecoRegions = ecoRegions.filterMetadata('ECO_ID', 'not_equals', update['ECO_ID']).merge(layer)

# for update in colorUpdates:
#     ecoRegions = ecoRegions.map(lambda f: f.set('style', {'color': f.get('COLOR'), 'width': 0}))
#     color_filtered = ecoRegions.filterMetadata('ECO_ID', 'equals', update['ECO_ID'])
#     color_updated = color_filtered.map(lambda f: f.set('style', {'color': update['COLOR'], 'width': 0}))
#     ecoRegions = ecoRegions.filterMetadata('ECO_ID', 'not_equals', update['ECO_ID']).merge(color_updated)


imageRGB = ecoRegions.style(styleProperty='style')

countries = countries.distinct('ADM0_CODE')
uniqueADM0Codes = countries.aggregate_array('ADM0_CODE').distinct()

# Define the directory paths
output_directory = 'img'
temp_directory = 'temp'


# for name in country_names:
#     country = countries.filter(ee.Filter.eq('ADM0_NAME', name))
#     print(country.get('ADM0_NAME').getInfo())

# x = 
# x = x.toInt()
def get_intersection_of_country_lists():
    total = 0
    adm0_codes = []
    for i in range(uniqueADM0Codes.size().toInt().getInfo()):
        adm0Code = ee.Number(uniqueADM0Codes.get(i))
        country = countries.filter(ee.Filter.eq('ADM0_CODE', adm0Code)).first()
        country_name = country.get('ADM0_NAME').getInfo()
        if country_name in country_names:
            total += 1

    print(total)
    return adm0_codes

# adm0_codes = get_intersection_of_country_lists()
for i in range(uniqueADM0Codes.size().toInt().getInfo()):
    adm0_code = ee.Number(uniqueADM0Codes.get(i))
    country = countries.filter(ee.Filter.eq('ADM0_CODE', adm0_code)).first()
    country_name = country.get('ADM0_NAME').getInfo()
    if country_name not in country_names:
        continue

    print(f"{country_name} - {adm0_code.getInfo()}")
    
    areaSquareKm = country.geometry().area().divide(1e6)
    areaString = str(areaSquareKm.round().getInfo())
    areaString = areaString[:-2]
    fileName = country.get('ADM0_NAME').getInfo().replace(' ', '') + '_' + areaString
    print(fileName)
    
    # Use bounds instead of the country's geometry
    # region = ee.geometry.Geometry.MultiPolygon(country.geometry())
    region = country.geometry().bounds()
    # print(region)
    layer = imageRGB.clip(region)
    # layer = layer.mask(region)
    scaleForExport = areaSquareKm.divide(5).getInfo()
    scaleForExport = 1000 if scaleForExport > 1000 else scaleForExport
    
    # layer = imageRGB.clipToBoundsAndScale(geometry=region, scale=scaleForExport)
    # Get the download URL
    download_url = layer.getDownloadURL({
        'name': fileName,
        # 'image': layer,
        'scale': scaleForExport, 
        # 'region': region.getInfo(), # Use getInfo() to convert the region to GeoJSON
        'format': 'GEO_TIFF'
    })

    # Download the image and save to the temp directory
    response = requests.get(download_url)
    
    # Ensure the directory exists
    os.makedirs(temp_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    # Save the image to the temp directory
    
    with open(os.path.join(temp_directory, f'{fileName}.tiff'), 'wb') as f:
        print('here')
        f.write(response.content)

    # Extract the contents of the zip file
    # subprocess.run(['unzip', '-o', os.path.join(temp_directory, f'{fileName}.tiffs'), '-d', temp_directory])
    
    # # Use gdal_merge.py to combine multiple GeoTIFF files into one
    # merged_tiff_path = os.path.join(temp_directory, f'{fileName.getInfo()}_merged.tif')
    # subprocess.run(['gdal_merge.py', '-o', merged_tiff_path] +
    #                [os.path.join(temp_directory, tiff_file) for tiff_file in os.listdir(temp_directory) if tiff_file.endswith('.tif')])

    # # Use gdal_translate to convert the merged GeoTIFF file to PNG
    # png_file_path = os.path.join(output_directory, f'{fileName.getInfo()}.png')
    # subprocess.run(['gdal_translate', '-of', 'PNG', merged_tiff_path, png_file_path])

    # # Remove temporary files
    # os.remove(os.path.join(temp_directory, f'{fileName.getInfo()}.zip'))
    # os.remove(merged_tiff_path)
    # for tiff_file in os.listdir(temp_directory):
    #     if tiff_file.endswith('.tif'):
    #         os.remove(os.path.join(temp_directory, tiff_file))


