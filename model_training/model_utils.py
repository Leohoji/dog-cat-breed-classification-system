import cv2
import math
import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path
from functools import partial
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.efficientnet import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input as EFNetPreProcessInput

class DataTransformer:
    def __init__(self, data_path:str):
        self.data_path = data_path
        
    def read_data(self) -> pd.DataFrame:
        """Read data via pandas module."""
        return pd.read_csv(self.data_path).loc[5:,]

    def preprocess(self) -> pd.DataFrame:
        """
        Preprocess data via following steps:
        1. Read data from a txt file of data_path, return a DataFrame.
        2. Process the columns via splitting operation.
        3. Drop unnecessary columns.
        4. Rename the columns to specific column names.
        5. Convert the object type to int type for further processing.
        6. Add suffix to the image columns with 'jpg' extension.
        7. Extract the classname/breed of the animal, create a new column for labels.

        Returns: DataFrame of preprocessed data.
        """
        df = self.read_data()
        df[['CLASS-ID','SPECIES','BREED','ID']] = df['#Image CLASS-ID SPECIES BREED ID'].str.split(expand=True) 
        df = df.drop('#Image CLASS-ID SPECIES BREED ID', axis=1)
        df = df.rename(columns={'CLASS-ID': 'IMAGE', 'SPECIES': 'CLASS_ID', 'BREED': 'SPECIES', 'ID': 'BREED_ID'})
        df[["CLASS_ID","SPECIES","BREED_ID"]] = df[["CLASS_ID","SPECIES","BREED_ID"]].astype(int)
        df['IMAGE'] = df['IMAGE'].apply(lambda x: str(x) + '.jpg')
        df = df.reset_index()
        df['CLASSNAME'] = df['IMAGE'].apply(lambda x: ' '.join(str(x).split('_')[:-1]))
        df = df.drop('index', axis=1)
        
        return df