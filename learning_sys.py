import base64
import numpy as np
import mysql.connector
from PIL import Image
from io import BytesIO
from pathlib import Path
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input as EFNetPreProcessInput

# ================================================================
# Additional packages for model training and fine-tuning
# ================================================================
from CatDogClassification.mysql_info import DATABASE_NAME, HOST, PORT, USER, PASSWORD
from training_data_info import DATA_PATH, ANNOTATION_PATH, TEST_PATH
from model_training.model_utils import DataTransformer, DataAugmentation
from model_training.model_utils import evaluate

time_now = lambda hours=0: dt.now() + relativedelta(hours=hours) # Set local time

IMG_SIZE = 224
INPUT_SHAPE = (IMG_SIZE, IMG_SIZE, 3)
BATCH_SIZE = 32

class LearningSystem():
    def __init__(self, 
                 species_for_train:str='cats',
                 DATA_PATH:str=DATA_PATH, 
                 ANNOTATION_DATA_PATH:str=ANNOTATION_PATH, 
                 fine_tune_ratio:float=0.05):
        """LearningSystem class object will fine-tune a pre-train model dependent on feedback from front-end interface."""
        self.species = species_for_train
        self.fine_tune_ratio = fine_tune_ratio
        
        self.SPECIES = 1 if (self.species == 'cats') else 2
        print(self.SPECIES)

        # Training parameters
        self.IMG_SIZE = 224
        self.BATCH_SIZE = 32
        self.DATA_PATH = DATA_PATH
        self.ANNOTATION_DATA_PATH = ANNOTATION_DATA_PATH
        
        # Real classes
        self.real_classes = np.load('.\\CatDogClassification\\label_data\\cats_classes.npy') \
                            if self.species == 'cats' \
                            else np.load('.\\CatDogClassification\\label_data\\dogs_classes.npy')
        self.new_model_name = '.\\CatDogClassification\\model_data\\new_classifier.h5'

    def get_all_historical_data(self):
        connection = mysql.connector.connect(host=HOST, 
                                            port=PORT,
                                            user=USER, 
                                            password=PASSWORD,
                                            database=DATABASE_NAME, 
                                            auth_plugin='mysql_native_password')
        cursor = connection.cursor()
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")
        query = f"SELECT * FROM `user_history`;"
        cursor.execute(query)
        historical_data = cursor.fetchall()
        cursor.close()
        connection.commit()
        connection.close()
        
        return historical_data
    
    def create_new_train_dataset(self):
        self.historical_data = self.get_all_historical_data()

        new_lines = []
        user_img_data = {}
        for idx, data in enumerate(self.historical_data):
            _, _, image, results, _ = data

            # create data for annotation file
            breed = results.split(",")[-1]
            if breed in self.real_classes:
                breed_ID_loc = np.where(self.real_classes == breed) 
                breed_ID = breed_ID_loc[0][0]+1
            else: continue
            fname = '{}_user{}-{}'.format(breed, idx, time_now().strftime(format='%Y%m%d-%H%M%S'))
            class_ID = '999'
            new_lines.append(f'{fname} {class_ID} {self.SPECIES} {breed_ID}')

            # create data for user's image read
            fPath = self.DATA_PATH.joinpath(fname + '.jpg')
            user_img_data[fPath] = image
        
        return (new_lines, user_img_data)

    def append_to_file(self, new_lines:list):
        """
        Append new information about image classification.
    
        Args:
            new_line: Content of image information
        """
        # Use append mode to add new content
        with open(self.ANNOTATION_DATA_PATH, 'a') as file:
            for new_line in new_lines:
                file.write(f'\n{new_line}')
                print(f'Add {new_line} info at {self.ANNOTATION_DATA_PATH}')

    def decode_and_save(self, user_img_data:dict):
        """
        Decode image from base64 byte into Numpy array, and save image.
    
        Args:
            fname: Path for image saving
        """
        for fPath, image in user_img_data.items():
            img_data = base64.b64decode(image)
            img = Image.open(BytesIO(img_data))
            img.save(fPath)
            print(f'Save image at {fPath}')

    def load_classifier(self):
        """Load pre-train model for fine-tuning"""
        if Path(self.new_model_name).is_file():
            classifier = tf.keras.models.load_model(self.new_model_name)
        else:
            if self.species == "cats":
                classifier = tf.keras.models.load_model('.\\CatDogClassification\\model_data\\cats_classifier.h5')
            else:
                classifier = tf.keras.models.load_model('.\\CatDogClassification\\model_data\\dogs_classifier.h5')
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

        # create training dataset
        self.new_lines, self.user_img_data = self.create_new_train_dataset()

        # Append to txt file  
        self.append_to_file(self.new_lines)

        # Save image into dataset
        self.decode_and_save(self.user_img_data)

        # Add image into folder and annotation txt
        self.data_transformer = DataTransformer(self.ANNOTATION_DATA_PATH)        

        # Data augmentation
        self.data_df = self.data_transformer.preprocess()
        self.df_species_df = self.data_df[self.data_df['SPECIES']==self.SPECIES]
        self.data_aug = DataAugmentation(dataframe=self.df_species_df, 
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
                            epochs=1,
                            validation_data=self.valid_data_gen)
    
        # Model evaluation
        species_path = Path(TEST_PATH).joinpath(self.species) # './test_images/%s' % (self.species)
        acc_score = evaluate(self.train_data_gen.class_indices, self.real_classes, species_path, self.classifier)
        print(f"Accuracy score on testing dataset: {acc_score}")

        # Save model
        # self.classifier.save(self.new_model_name)
        print(f'New classifier has been save at {self.new_model_name}')
    

if __name__ == '__main__':    
    cat_learning_sys = LearningSystem('cats')
    dog_learning_sys = LearningSystem('dogs')
    cat_learning_sys.fine_tune_classifier()
    # dog_learning_sys.fine_tune_classifier()
