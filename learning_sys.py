import cv2
import math
import json
import base64
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
from pathlib import Path
from functools import partial
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input as EFNetPreProcessInput

from model_training.model_utils import DataTransformer, DataAugmentation
from model_training.train import preprocess_image, create_dataset, calculate_accuracy, evaluate

time_now = lambda hours=0: dt.now() + relativedelta(hours=hours) # Set local time




def compress_image_to_base64(input_image_path:str, 
                             quality:int=100):
    """
    Compress image into base64 data type.
    1. Open the image using OpenCV
    2. Convert image from BGR to RGB (OpenCV uses BGR by default)
    3. Convert the image to PIL format
    4. Use BytesIO to store the compressed image in memory
    5. Compress the image and save it to the memory's BytesIO object instead of disk
    6. Convert the compressed image data in BytesIO to base64
    """
    img = cv2.imread(input_image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    buffered = BytesIO()
    img_pil.save(buffered, format="JPEG", quality=quality)
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return img_base64
    

if __name__ == '__main__':    
    species = 'cats'
    test_image_path = 'Bengal.jpg'
    image = compress_image_to_base64(test_image_path)
    result = 'no'
    breed = 'Bengal'
    feedback = {'species': species, 'image': image, 'result': result, 'breed': breed}