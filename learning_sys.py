import cv2
import json
import base64
import numpy as np
from PIL import Image
from io import BytesIO
from pathlib import Path
from copy import deepcopy
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input as EFNetPreProcessInput

from model_training.model_utils import DataTransformer, DataAugmentation
from model_training.train import evaluate
from model import DatabaseManager

time_now = lambda hours=0: dt.now() + relativedelta(hours=hours) # Set local time

DATASET_DIR = 'C:\\Users\\User\\Desktop\\cat_dog_dataset'
DATA_PATH = Path(DATASET_DIR).joinpath('Cats_and_Dogs_Breeds_Classification_Oxford_Dataset\\images\\images')
ANNOTATION_PATH = Path(DATASET_DIR).joinpath('Cats_and_Dogs_Breeds_Classification_Oxford_Dataset\\annotations\\annotations\\list.txt')
TEST_PATH = Path(DATASET_DIR).joinpath('test_images')
IMG_SIZE = 224
INPUT_SHAPE = (IMG_SIZE, IMG_SIZE, 3)
BATCH_SIZE = 32

class LearningSystem(DatabaseManager):
    def __init__(self, user_name:str, feedback:json, DATA_PATH:str, ANNOTATION_DATA_PATH:str, fine_tune_ratio:float=0.05):
        """LearningSystem class object will fine-tune a pre-train model dependent on feedback from front-end interface."""
        self.user_name = user_name
        self.feedback = json.loads(feedback)
        self.fine_tune_ratio = fine_tune_ratio
        
        # Training parameters
        self.IMG_SIZE = 224
        self.BATCH_SIZE = 32
        self.DATA_PATH = DATA_PATH
        self.ANNOTATION_DATA_PATH = ANNOTATION_DATA_PATH

        self.species = self.feedback['species']
        self.image = self.feedback['image']
        self.result = self.feedback['result']
        self.breed = self.feedback['breed']
        
        self.real_classes = np.load('cats_classes.npy') if self.species == 'cats' else np.load('dogs_classes.npy')
        self.new_model_name = self.species + '_classifier_new.h5'

    def append_to_file(self, new_line:str):
        """
        Append new information about image classification.
    
        Args:
            new_line: Content of image information
        """
        # Use append mode to add new content
        with open(self.ANNOTATION_DATA_PATH, 'a') as file:
            file.write(f'\n{new_line}')
        print(f'Add {new_line} info at {self.ANNOTATION_DATA_PATH}')

    def decode_and_save(self, fPath:str):
        """
        Decode image from base64 byte into Numpy array, and save image.
    
        Args:
            fname: Path for image saving
        """
        img_data = base64.b64decode(self.image)
        img = Image.open(BytesIO(img_data))
        img.save(fPath)
        print(f'Save image at {fPath}')

    def load_classifier(self):
        """Load pre-train model for fine-tuning"""
        if Path(self.new_model_name).is_file():
            classifier = tf.keras.models.load_model(self.new_model_name)
        else:
            classifier = tf.keras.models.load_model('cats_classifier.h5')

        return classifier

    def unfreeze(self):
        fine_tune_base_model = self.classifier.layers[1]
        layer_number = -int(len(fine_tune_base_model.layers) * self.fine_tune_ratio)
        
        # Unfreeze all of the layers in the base model
        fine_tune_base_model.trainable = True
        
        # Refreeze every layer except for the last 5
        for layer in fine_tune_base_model.layers[:layer_number]:
            layer.trainable = False
        
    def fine_tune_classifier(self):
        """Fine-tune animal breed classifier"""
        # Set random seed and clear session
        seed = 42
        np.random.seed(seed)
        tf.random.set_seed(seed)
        tf.keras.backend.clear_session()

        fname = self.breed + '_' + time_now().strftime(format='%Y%m%d-%H%M%S')
        save_path = fname + '.jpg'
        CLASS_ID = '999'
        SPECIES = 1 if self.species == 'cats' else 2
        BREED_ID = np.where(self.real_classes == self.breed)[0][0]+1

        # Append to txt file  
        self.append_to_file(f'{fname} {CLASS_ID} {SPECIES} {BREED_ID}')

        # Save image into dataset
        self.decode_and_save(fPath=self.DATA_PATH.joinpath(save_path))

        # Add image into folder and annotation txt
        self.data_transformer = DataTransformer(self.ANNOTATION_DATA_PATH)        

        # Data augmentation
        self.data_df = self.data_transformer.preprocess()
        self.data_with_feedback_df = self.data_df[self.data_df['SPECIES'] == SPECIES]
        self.data_aug = DataAugmentation(dataframe=self.data_with_feedback_df, 
                                         img_data_path=self.DATA_PATH, 
                                         img_size=self.IMG_SIZE, 
                                         batch_size=self.BATCH_SIZE, 
                                         preprocess_function=EFNetPreProcessInput)
        
        self.train_data_gen, self.valid_data_gen = self.data_aug.create_flow()

        # Model loading
        self.classifier = self.load_classifier()
        self.unfreeze()

        # Compile model
        self.classifier.compile(loss='categorical_crossentropy', 
                                optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5), 
                                metrics=['accuracy'])
        # Train model
        self.classifier.fit(self.train_data_gen, 
                            epochs=3,
                            validation_data=self.valid_data_gen)
    
        # Model evaluation
        species_path = './test_images/%s' % (species)
        acc_score = evaluate(self.train_data_gen.class_indices, self.real_classes, species_path, self.classifier)
        print(f"Accuracy score on testing dataset: {acc_score}")

        # Save model
        self.classifier.save(self.new_model_name)
        print(f'New classifier has been save at {self.new_model_name}')
        
        # Update to database
        feedback_backup = deepcopy(self.feedback)
        del feedback_backup['image']
        self._save = self.update_historical_data(self.user_name, self.image, feedback_backup)
        print('OK', self._save)


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

    Args:
        input_image_path: Path for image excepted to be compressed
        quality: Image quality for image compression
    Returns:
        Compressed image in base64 byte format
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