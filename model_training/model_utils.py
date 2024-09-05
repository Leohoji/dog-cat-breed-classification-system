import cv2
import math
import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path
from functools import partial
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
    
class DataAugmentation:
    def __init__(self, 
                 dataframe:pd.DataFrame, 
                 img_data_path:str, 
                 img_size:int=224, 
                 batch_size:int=32, 
                 preprocess_function=EFNetPreProcessInput):
        self.dataframe = dataframe
        self.DATA_PATH = img_data_path
        self.IMG_SIZE = img_size
        self.BATCH_SIZE = batch_size
        self.preprocess_function = preprocess_function
        self.IMG_SHAPE = (self.IMG_SIZE, self.IMG_SIZE)
        self.train_datagen, self.valid_datagen = self.data_generator()
        
    def data_generator(self):
        """Generate data via ImageDataGenerator object."""
        train_datagen = ImageDataGenerator(preprocessing_function=self.preprocess_function,
                                           shear_range=0.2,
                                           zoom_range=0.2,
                                           horizontal_flip=True,
                                           vertical_flip=True,
                                           validation_split=0.2,
                                           rotation_range=90,
                                           width_shift_range=0.2, 
                                           height_shift_range=0.2)
        
        valid_datagen = ImageDataGenerator(preprocessing_function=self.preprocess_function, 
                                           validation_split=0.2)

        return (train_datagen, valid_datagen)

    def create_flow(self):
        """Create flow data of data generator."""
        self.train_gen_flow = self.train_datagen.flow_from_dataframe(dataframe=self.dataframe,
                                                                     directory=self.DATA_PATH,
                                                                     x_col='IMAGE',
                                                                     y_col='CLASSNAME',
                                                                     target_size=self.IMG_SHAPE,
                                                                     batch_size=self.BATCH_SIZE,
                                                                     class_mode="categorical",
                                                                     subset='training',
                                                                     shuffle=True)
    
        self.valid_gen_flow = self.valid_datagen.flow_from_dataframe(dataframe=self.dataframe,
                                                                     directory=self.DATA_PATH,
                                                                     x_col='IMAGE',
                                                                     y_col='CLASSNAME',
                                                                     target_size=self.IMG_SHAPE,
                                                                     batch_size=self.BATCH_SIZE,
                                                                     class_mode="categorical",
                                                                     subset='validation', 
                                                                     shuffle=False)
        return (self.train_gen_flow, self.valid_gen_flow)