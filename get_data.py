import ee
import os
import requests
import math
from pathlib import Path
from ee import feature

def get_images():
    # list of country names we care about
    country_names = ['Andorra', 'United Arab Emirates', 'Afghanistan', 'Antigua and Barbuda', 'Anguilla', 'Albania', 'Armenia', 'Angola', 'Antarctica', 'Argentina', 'American Samoa', 'Austria', 'Australia', 'Aruba', 'Åland Islands', 'Azerbaijan', 'Bosnia and Herzegovina', 'Barbados', 'Bangladesh', 'Belgium', 'Burkina Faso', 'Bulgaria', 'Bahrain', 'Burundi', 'Benin', 'Saint Barthélemy', 'Bermuda', 'Brunei Darussalam', 'Bolivia, Plurinational State of', 'Bonaire, Sint Eustatius and Saba', 'Brazil', 'Bahamas', 'Bhutan', 'Bouvet Island', 'Botswana', 'Belarus', 'Belize', 'Canada', 'Cocos (Keeling) Islands', 'Congo, Democratic Republic of the', 'Central African Republic', 'Congo', 'Switzerland', 'Côte d\'Ivoire', 'Cook Islands', 'Chile', 'Cameroon', 'China', 'Colombia', 'Costa Rica', 'Cuba', 'Cabo Verde', 'Curaçao', 'Christmas Island', 'Cyprus', 'Czechia', 'Germany', 'Djibouti', 'Denmark', 'Dominica', 'Dominican Republic', 'Algeria', 'Ecuador', 'Estonia', 'Egypt', 'Western Sahara', 'Eritrea', 'Spain', 'Ethiopia', 'Finland', 'Fiji', 'Falkland Islands (Malvinas)', 'Micronesia, Federated States of', 'Faroe Islands', 'France', 'Gabon', 'United Kingdom of Great Britain and Northern Ireland', 'Grenada', 'Georgia', 'French Guiana', 'Guernsey', 'Ghana', 'Gibraltar', 'Greenland', 'Gambia', 'Guinea', 'Guadeloupe', 'Equatorial Guinea', 'Greece', 'South Georgia and the South Sandwich Islands', 'Guatemala', 'Guam', 'Guinea-Bissau', 'Guyana', 'Hong Kong', 'Heard Island and McDonald Islands', 'Honduras', 'Croatia', 'Haiti', 'Hungary', 'Indonesia', 'Ireland', 'Israel', 'Isle of Man', 'India', 'British Indian Ocean Territory', 'Iraq', 'Iran, Islamic Republic of', 'Iceland', 'Italy', 'Jersey', 'Jamaica', 'Jordan', 'Japan', 'Kenya', 'Kyrgyzstan', 'Cambodia', 'Kiribati', 'Comoros', 'Saint Kitts and Nevis', 'Korea, Democratic People\'s Republic of', 'Korea, Republic of', 'Kuwait', 'Cayman Islands', 'Kazakhstan', 'Lao People\'s Democratic Republic', 'Lebanon', 'Saint Lucia', 'Liechtenstein', 'Sri Lanka', 'Liberia', 'Lesotho', 'Lithuania', 'Luxembourg', 'Latvia', 'Libya', 'Morocco', 'Monaco', 'Moldova, Republic of', 'Montenegro', 'Saint Martin, (French part)', 'Madagascar', 'Marshall Islands', 'North Macedonia', 'Mali', 'Myanmar', 'Mongolia', 'Macao', 'Northern Mariana Islands', 'Martinique', 'Mauritania', 'Montserrat', 'Malta', 'Mauritius', 'Maldives', 'Malawi', 'Mexico', 'Malaysia', 'Mozambique', 'Namibia', 'New Caledonia', 'Niger', 'Norfolk Island', 'Nigeria', 'Nicaragua', 'Netherlands', 'Norway', 'Nepal', 'Nauru', 'Niue', 'New Zealand', 'Oman', 'Panama', 'Peru', 'French Polynesia', 'Papua New Guinea', 'Philippines', 'Pakistan', 'Poland', 'Saint Pierre and Miquelon', 'Pitcairn', 'Puerto Rico', 'Palestine, State of', 'Portugal', 'Palau', 'Paraguay', 'Qatar', 'Réunion', 'Romania', 'Serbia', 'Russian Federation', 'Rwanda', 'Saudi Arabia', 'Solomon Islands', 'Seychelles', 'Sudan', 'Sweden', 'Singapore', 'Saint Helena, Ascension and Tristan da Cunha', 'Slovenia', 'Svalbard and Jan Mayen', 'Slovakia', 'Sierra Leone', 'San Marino', 'Senegal', 'Somalia', 'Suriname', 'South Sudan', 'Sao Tome and Principe', 'El Salvador', 'Sint Maarten, (Dutch part)', 'Syrian Arab Republic', 'Eswatini', 'Turks and Caicos Islands', 'Chad', 'French Southern Territories', 'Togo', 'Thailand', 'Tajikistan', 'Tokelau', 'Timor-Leste', 'Turkmenistan', 'Tunisia', 'Tonga', 'Türkiye', 'Trinidad and Tobago', 'Tuvalu', 'Taiwan, Province of China', 'Tanzania, United Republic of', 'Ukraine', 'Uganda', 'United States Minor Outlying Islands', 'United States of America', 'Uruguay', 'Uzbekistan', 'Holy See', 'Saint Vincent and the Grenadines', 'Venezuela, Bolivarian Republic of', 'Virgin Islands, British', 'Virgin Islands, U.S.', 'Viet Nam', 'Vanuatu', 'Wallis and Futuna', 'Samoa', 'Yemen', 'Mayotte', 'South Africa', 'Zambia', 'Zimbabwe']
    i    = set(country_names)

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


def load_DB():

    """
    For each image we have, use ADMO_Code (filename) to lookup and construct JSON:
        { name : iran
        total area : alot
        ecoregion1 : 45%,
        ecoregion2 : 18%,
        ....
    """

    data = {}
    def add_to_DB(data):
        pass

    # Authenticate to the Earth Engine servers
    ee.Initialize()

    countries = ee.FeatureCollection('FAO/GAUL/2015/level0')
    ecoRegions = ee.FeatureCollection('RESOLVE/ECOREGIONS/2017')
    countries = countries.distinct('ADM0_CODE')

    img_path = Path('img_png')
    for file_path in img_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".png":
            entry = {'eco_data':{}}
            adm0_code = int(file_path.stem)
            # adm0_code = 146
            country = countries.filter(ee.Filter.eq('ADM0_CODE', adm0_code)).first()
            entry['adm0_code'] = adm0_code


            bounds = country.geometry()
            country_ecoregions = ecoRegions.filterBounds(bounds)
            country_area = bounds.area().getInfo() #sq meters
            x = country_ecoregions.getInfo()

            print(country_area)
            def calc_relative_area(feature):
                # area = feature.geometry().area()
                # return feature.set({'area': area, 'Relative_Area': relative_area})
                # x = feature.intersection()
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
            entry['eco_data']['area_sum'] = area_sum
            data[country.get('ADM0_NAME').getInfo()] = entry
            print(data)
    # print(data)


load_DB()
