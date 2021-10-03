from os import path
from typing import Tuple

import numpy as np
import pandas as pd

from physicalrisk.handler.constants.constants import RESOLUTION, FUTURE_MONTH
#from physicalrisk.handler.AWSdata import aws
from physicalrisk.handler.raster_handler.rasterhandler import RasterHandler
from physicalrisk.handler.printMessageHandler.formatePrint import Formatter

import platform
import boto3
s3 = boto3.resource(
    service_name='s3',
    region_name='eu-west-2',
    aws_access_key_id='AKIAYHM23ZQQ4JOTA34C',
    aws_secret_access_key='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'
)
class Data_Handler():

    def __init__(self):
        self.column_names = self.create_column_names(
            {'elevation': 9, 'precipitation': 9})
        self.df_to_predict = pd.DataFrame(columns=self.column_names)
        self.scenarios_based_future_precipitation = {
            1: 'WorldClim/FuturePrecipitation/wc2.1_2.5m_prec_CNRM-CM6-1_ssp126_2021-2040.tif',
            2: 'WorldClim/FuturePrecipitation/wc2.1_2.5m_prec_CNRM-CM6-1_ssp245_2021-2040.tif'
        }

    def build_prediction_data(self, input_long_lat: list, scenario):

        future_precip_ml = self.load_future_precipitation(input_long_lat[0], input_long_lat[1], scenario)
        future_elevation_ml = self.add_in_elevation_feature(input_long_lat[0], input_long_lat[1])

        new_future_flood_features = pd.DataFrame(np.append(future_elevation_ml, future_precip_ml)).T
        new_future_flood_features.columns = self.column_names
        df_to_predict = self.df_to_predict.append(new_future_flood_features)

        df_to_predict.reset_index(inplace=True)
        df_to_predict.drop('index', axis=1, inplace=True)

        Formatter.green(f"Added precipitation and elevation data for {len(df_to_predict)} location successfully!")
        return df_to_predict

    def flood_depth(self, input_long_lat: list):
        # This is the elevation feature for the current flood\
        resolution = 0.5
        elevation_data, elevation_meta = self.get_raster_feature('WorldClim/Elevation/wc2.1_30s_elev.tif', input_long_lat[0],input_long_lat[1], resolution)
        elevation_diff = elevation_data.reshape(1, -1)
        elevation_diff = elevation_diff - elevation_diff[0][4] #calculate elevation difference between location lat-long and its surrounding pixels
        elevation_diff = elevation_diff.tolist()[0]
        del elevation_diff[4] 
        flood_depth = np.mean(elevation_diff) #take the minimum difference as the flood depth
        if flood_depth < 0:
            flood_depth = 0
        return flood_depth

    @staticmethod
    def create_column_names(prefixes: dict) -> list:
        columns_out = []
        for k in prefixes:
            for i in range(prefixes[k]):
                i += 1
                columns_out.append(f'{k}_{str(i).zfill(2)}')
        return columns_out

    def load_future_precipitation(self, longitude: float, latitude: float, scenario):
        # TODO: Should incorporate all months into output instead of just January

        future_precipitation = self.scenarios_based_future_precipitation.get(scenario, "invalid scenario")

        future_precipitation_data, _ = self.get_raster_feature(future_precipitation, longitude, latitude,
                                                               RESOLUTION)
        #future_precipitation_data = future_precipitation_data[FUTURE_MONTH]
        future_precipitation_data = future_precipitation_data.reshape(1, -1)
        return future_precipitation_data

    def add_in_elevation_feature(self, longitude: float, latitude: float):
        # This is the elevation feature for the current flood
        # TODO: Questions: what does get raster feature do?
        #   what is AWSdata properties of elevation AWSdata (meter): tif file: array of value: pixel, get raster feature: convert lat, lon to certain pixel, take AWSdata from pixel, rearrange pixel
        #   put them into one by nine array.
        elevation_data, _ = self.get_raster_feature('WorldClim/Elevation/wc2.1_2.5m_elev.tif', longitude, latitude, RESOLUTION)
        elevation_ml = elevation_data.reshape(1, -1)
        # calculate the related 9 elevation point to the non-flood centroid
        # elevation_ml = elevation_ml - elevation_ml[0][4]
        return elevation_ml

    def get_raster_feature(self, feature_filename: str, longitude: float, latitude: float, resolution: float) -> Tuple[
        np.array, dict]:
        bounds = self.get_raster_bounds(latitude, longitude, resolution)
        # feature_filepath = path.join(settings.dataroot, feature_filename)  # location of AWSdata
        # feature_filename with /is a absolute file path, so previous componnet settings.dataroot is discarded
        feature, lons, lats = RasterHandler.read_crop_geotif(path.join('/vsis3/bci-physical-risk-model/', feature_filename), bounds)
        metadata = {
            'lons': lons,
            'lats': lats
        }
        return feature, metadata

    def get_raster_bounds(self, lat, long, resolution):
        bounds = [[long - 1 * resolution / 60, lat - 1 * resolution / 60],
                  [long + 1 * resolution / 60, lat + 1 * resolution / 60]]
        return bounds
