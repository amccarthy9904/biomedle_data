import ee
import os
import requests
import math
from decimal import Decimal
from pathlib import Path
import boto3
import json

def get_colors():
    ee.Initialize()

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

    colors = {}
    biomes = ['Deserts & Xeric Shrublands', 'N/A', 'Tropical & Subtropical Moist Broadleaf Forests', 'Mediterranean Forests, Woodlands & Scrub', 'Temperate Broadleaf & Mixed Forests', 'Tropical & Subtropical Coniferous Forests', 'Temperate Conifer Forests', 'Boreal Forests/Taiga', 'Flooded Grasslands & Savannas', 'Temperate Grasslands, Savannas & Shrublands', 'Montane Grasslands & Shrublands', 'Tropical & Subtropical Dry Broadleaf Forests', 'Tropical & Subtropical Grasslands, Savannas & Shrublands', 'Mangroves', 'Tundra']
    for biome in biomes:
        targetFeatures = ecoRegions.filter(ee.Filter.eq('BIOME_NAME', biome))
        targetFeature = ee.Feature(targetFeatures.first())
        color = targetFeature.get('COLOR')
        colors[biome] = color.getInfo()
    
    print(colors)

def get_images():
    # list of country names we care about
    country_names = ['Andorra', 'United Arab Emirates', 'Afghanistan', 'Antigua and Barbuda', 'Anguilla', 'Albania', 'Armenia', 'Angola', 'Antarctica', 'Argentina', 'American Samoa', 'Austria', 'Australia', 'Aruba', 'Åland Islands', 'Azerbaijan', 'Bosnia and Herzegovina', 'Barbados', 'Bangladesh', 'Belgium', 'Burkina Faso', 'Bulgaria', 'Bahrain', 'Burundi', 'Benin', 'Saint Barthélemy', 'Bermuda', 'Brunei Darussalam', 'Bolivia, Plurinational State of', 'Bonaire, Sint Eustatius and Saba', 'Brazil', 'Bahamas', 'Bhutan', 'Bouvet Island', 'Botswana', 'Belarus', 'Belize', 'Canada', 'Cocos (Keeling) Islands', 'Congo, Democratic Republic of the', 'Central African Republic', 'Congo', 'Switzerland', 'Côte d\'Ivoire', 'Cook Islands', 'Chile', 'Cameroon', 'China', 'Colombia', 'Costa Rica', 'Cuba', 'Cabo Verde', 'Curaçao', 'Christmas Island', 'Cyprus', 'Czechia', 'Germany', 'Djibouti', 'Denmark', 'Dominica', 'Dominican Republic', 'Algeria', 'Ecuador', 'Estonia', 'Egypt', 'Western Sahara', 'Eritrea', 'Spain', 'Ethiopia', 'Finland', 'Fiji', 'Falkland Islands (Malvinas)', 'Micronesia, Federated States of', 'Faroe Islands', 'France', 'Gabon', 'United Kingdom of Great Britain and Northern Ireland', 'Grenada', 'Georgia', 'French Guiana', 'Guernsey', 'Ghana', 'Gibraltar', 'Greenland', 'Gambia', 'Guinea', 'Guadeloupe', 'Equatorial Guinea', 'Greece', 'South Georgia and the South Sandwich Islands', 'Guatemala', 'Guam', 'Guinea-Bissau', 'Guyana', 'Hong Kong', 'Heard Island and McDonald Islands', 'Honduras', 'Croatia', 'Haiti', 'Hungary', 'Indonesia', 'Ireland', 'Israel', 'Isle of Man', 'India', 'British Indian Ocean Territory', 'Iraq', 'Iran, Islamic Republic of', 'Iceland', 'Italy', 'Jersey', 'Jamaica', 'Jordan', 'Japan', 'Kenya', 'Kyrgyzstan', 'Cambodia', 'Kiribati', 'Comoros', 'Saint Kitts and Nevis', 'Korea, Democratic People\'s Republic of', 'Korea, Republic of', 'Kuwait', 'Cayman Islands', 'Kazakhstan', 'Lao People\'s Democratic Republic', 'Lebanon', 'Saint Lucia', 'Liechtenstein', 'Sri Lanka', 'Liberia', 'Lesotho', 'Lithuania', 'Luxembourg', 'Latvia', 'Libya', 'Morocco', 'Monaco', 'Moldova, Republic of', 'Montenegro', 'Saint Martin, (French part)', 'Madagascar', 'Marshall Islands', 'North Macedonia', 'Mali', 'Myanmar', 'Mongolia', 'Macao', 'Northern Mariana Islands', 'Martinique', 'Mauritania', 'Montserrat', 'Malta', 'Mauritius', 'Maldives', 'Malawi', 'Mexico', 'Malaysia', 'Mozambique', 'Namibia', 'New Caledonia', 'Niger', 'Norfolk Island', 'Nigeria', 'Nicaragua', 'Netherlands', 'Norway', 'Nepal', 'Nauru', 'Niue', 'New Zealand', 'Oman', 'Panama', 'Peru', 'French Polynesia', 'Papua New Guinea', 'Philippines', 'Pakistan', 'Poland', 'Saint Pierre and Miquelon', 'Pitcairn', 'Puerto Rico', 'Palestine, State of', 'Portugal', 'Palau', 'Paraguay', 'Qatar', 'Réunion', 'Romania', 'Serbia', 'Russia', 'Rwanda', 'Saudi Arabia', 'Solomon Islands', 'Seychelles', 'Sudan', 'Sweden', 'Singapore', 'Saint Helena, Ascension and Tristan da Cunha', 'Slovenia', 'Svalbard and Jan Mayen', 'Slovakia', 'Sierra Leone', 'San Marino', 'Senegal', 'Somalia', 'Suriname', 'South Sudan', 'Sao Tome and Principe', 'El Salvador', 'Sint Maarten, (Dutch part)', 'Syrian Arab Republic', 'Eswatini', 'Turks and Caicos Islands', 'Chad', 'French Southern Territories', 'Togo', 'Thailand', 'Tajikistan', 'Tokelau', 'Timor-Leste', 'Turkmenistan', 'Tunisia', 'Tonga', 'Türkiye', 'Trinidad and Tobago', 'Tuvalu', 'Taiwan, Province of China', 'Tanzania, United Republic of', 'Ukraine', 'Uganda', 'United States Minor Outlying Islands', 'United States of America', 'Uruguay', 'Uzbekistan', 'Holy See', 'Saint Vincent and the Grenadines', 'Venezuela, Bolivarian Republic of', 'Virgin Islands, British', 'Virgin Islands, U.S.', 'Viet Nam', 'Vanuatu', 'Wallis and Futuna', 'Samoa', 'Yemen', 'Mayotte', 'South Africa', 'Zambia', 'Zimbabwe']
    country_names = set(country_names)

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


    imageRGB = ecoRegions.style(styleProperty='style')

    countries = countries.distinct('ADM0_CODE')
    uniqueADM0Codes = countries.aggregate_array('ADM0_CODE').distinct()

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

    def to_drive(image, file_name, region, scale):
        task = ee.batch.Export.image.toDrive(
        image=image,
        description=file_name,
        folder='biomedle',
        region=region,
        scale=scale,
        )

        task.start()

    def download(file_name, scale, region, image):
        """
        clipping an image when using this method seems to not work
        do not attempt
        """
        download_url = image.getDownloadURL({
            'name': file_name,
            # 'image': layer,
            # 'scale': scale, 
            'region': region, # Use getInfo() to convert the region to GeoJSON
            'format': 'GEO_TIFF'
        })

        response = requests.get(download_url)

        # Define the directory paths
        # Dont need to do this for every image
        png_directory = 'img_tif'
        tiff_directory = 'img_png'

        # Ensure the directory exists
        os.makedirs(png_directory, exist_ok=True)
        os.makedirs(tiff_directory, exist_ok=True)

        # Save the image to the tiff directory
        with open(os.path.join(tiff_directory, f'{fileName}.tiff'), 'wb') as f:
            f.write(response.content)


    for i in range(uniqueADM0Codes.size().toInt().getInfo()):
        adm0_code = ee.Number(uniqueADM0Codes.get(i))
        country = countries.filter(ee.Filter.eq('ADM0_CODE', adm0_code)).first()
        country_name = country.get('ADM0_NAME').getInfo()
        if country_name not in country_names:
            continue
        
        areaSquareKm = country.geometry().area().divide(1e6)
        areaString = str(areaSquareKm.round().getInfo())
        areaString = areaString[:-2]
        fileName = str(adm0_code.getInfo())
        scale = areaSquareKm.getInfo()
        scale = math.sqrt(scale)
        
        region = country.geometry()
        image = imageRGB.clip(region)
        
        to_drive(image, fileName, region, scale)


def create_country_data(to_skip):

    """
    For each image we have, use ADMO_Code (filename) to lookup and construct JSON:
        {'Liechtenstein': 
            {'eco_data': 
                {'Temperate Broadleaf & Mixed Forests': 0.27811180614514314, 
                'Temperate Conifer Forests': 0.7218881938568292, 
                'area_sum': 1.0000000000019724}, 
            'adm0_code': 146, 
            'total_area': 150535189.52041718}}
        ....
    """
    
    ee.Initialize()

    countries = ee.FeatureCollection('FAO/GAUL/2015/level0')
    ecoRegions = ee.FeatureCollection('RESOLVE/ECOREGIONS/2017')
    countries = countries.distinct('ADM0_CODE')

    img_path = Path('img_png')
    
    paths = [path for path in img_path.iterdir()]
    for file_path in paths:
    # for file_path in reversed(paths):
        if file_path.is_file() and file_path.suffix.lower() == ".png":
            
            adm0_code = int(file_path.stem)
            country = countries.filter(ee.Filter.eq('ADM0_CODE', adm0_code)).first()
            country_name = country.get('ADM0_NAME').getInfo().lower()
            print(country_name)
            if country_name in to_skip:
                continue

            entry = {'country': country_name, 'eco_data': {}}

            bounds = country.geometry()
            country_ecoregions = ecoRegions.filterBounds(bounds)
            country_area = bounds.area().getInfo()
            def calc_relative_area(feature):
                overlap = ee.feature.Feature.intersection(feature, country)
                area = overlap.area()
                relative_area = ee.Number(area).divide(bounds.area())
                return feature.set({'area': area, 'Relative_Area': relative_area})

            country_ecoregions_with_relative_area = country_ecoregions.map(calc_relative_area)
            cerra = country_ecoregions_with_relative_area.getInfo()
            area_sum = 0
            for feature in cerra['features']:
                if feature['properties']['BIOME_NAME'] in entry['eco_data']:
                    entry['eco_data'][feature['properties']['BIOME_NAME']] += feature['properties']['Relative_Area']
                else:
                    entry['eco_data'][feature['properties']['BIOME_NAME']] = feature['properties']['Relative_Area']
                area_sum += feature['properties']['Relative_Area']

            # make sure all areas add to 1 and 
            for eco_area in entry['eco_data'].keys():
                entry['eco_data'][eco_area] = entry['eco_data'][eco_area] / area_sum 
            
            # replace N/A with Rocks and Ice
            if 'N/A' in entry['eco_data']:
                entry['eco_data']['Rocks and Ice'] = entry['N/A'][eco_area]
                del entry['eco_data'][eco_area]

            entry['total_area'] = country_area
            print(country_name)
            save_data(country_name, entry)
            

def save_data(name, data):
    with open(f'country_json/{name}.json','w') as country_file:
        country_file.write(json.dumps(data, indent='  '))

def load_db_from_files():
    dynamodb = boto3.resource('dynamodb') 
    json_path = Path('country_json')
    for file_path in json_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".json":
            with open(file_path) as country_data:
                d = json.load(country_data)
                add_to_DB(dynamodb, d)
            
def add_to_DB(db, data):
    table = db.Table('country')
    item = json.loads(json.dumps(data), parse_float=Decimal)
    response = table.put_item(Item = item)
    print(f"{item['country']} - {response}")


to_skip = set()
json_path = Path('country_json')
for file_path in json_path.iterdir():
    to_skip.add(file_path.stem)


# get_colors()
create_country_data(to_skip)
load_db_from_files()
