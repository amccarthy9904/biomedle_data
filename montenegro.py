import ee
from geemap import Map, ee_export_image, ee_to_numpy

import numpy as np
import matplotlib.pyplot as plt


# Authenticate with your Earth Engine account
ee.Initialize()

# Load the countries and ecoregions datasets
countries = ee.FeatureCollection('FAO/GAUL/2015/level0')
ecoRegions = ee.FeatureCollection('RESOLVE/ECOREGIONS/2017')

# Filter the countries dataset to get Montenegro
montenegro = countries.filter(ee.Filter.eq('ADM0_NAME', 'Montenegro'))

# Filter ecoregions to get only those within Montenegro
ecoRegionsMontenegro = ecoRegions.filterBounds(montenegro)

# Create an image for each ecoregion
def create_ecoregion_image(feature):
    ecoregion_image = ee.Image.constant(0).byte().paint(ee.FeatureCollection([feature]), 1)
    return ecoregion_image.set('ECO_NAME', feature.get('ECO_NAME'))

# Map over the ecoregions to create a collection of images
ecoregion_images = ecoRegionsMontenegro.map(create_ecoregion_image)

# Mosaic the images into a single image
image = ee.ImageCollection(ecoregion_images).mosaic()

# Define visualization parameters
palette = ['red', 'green', 'blue', 'purple', 'orange', 'yellow', 'brown', 'pink', 'gray', 'cyan']
vis_params = {
    'min': 0,
    'max': 9,
    'palette': palette
}

# # Export the image as an asset
image_task = ee_export_image(
    image,
    filename='montenegro_ecoregions.tif',
    region=montenegro.geometry(),
    scale=300,
    crs='EPSG:4326'
)

