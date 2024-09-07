import cv2
import numpy as np
import tensorflow as tf
from pathlib import Path
from model_utils import DataTransformer, DataAugmentation, AnimalClassifier
from tensorflow.keras.applications.efficientnet import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input as EFNetPreProcessInput

DATASET_DIR = 'C:\\Users\\User\\Desktop\\(cat-dog)_model_training'
DATA_PATH = Path(DATASET_DIR).joinpath('Cats_and_Dogs_Breeds_Classification_Oxford_Dataset\\images\\images')
ANNOTATION_PATH = Path(DATASET_DIR).joinpath('Cats_and_Dogs_Breeds_Classification_Oxford_Dataset\\annotations\\annotations\\list.txt')
TEST_PATH = Path(DATASET_DIR).joinpath('test_images')
IMG_SIZE = 224
INPUT_SHAPE = (IMG_SIZE, IMG_SIZE, 3)
BATCH_SIZE = 32

def get_classes(class_indices:dict, save_path='') -> list:
    """
    Get animal classes from class indices of dictionary.

    Args:
        class_indices: Class indices in dictionary data type.
    Returns: 
        Class names in list data type.
    """
    pairs = [(cls_name, index) for cls_name, index in class_indices.items()] # convert to list with tuple
    pairs_sorted = sorted(pairs, key=lambda pairs: pairs[1]) # sorting values
    classes = np.array([pair_cls[0] for pair_cls in pairs_sorted]) # convert to numpy array
    if save_path: np.save(save_path, classes) # save labels

    return classes

def preprocess_image(image_path:str, size:tuple=(IMG_SIZE, IMG_SIZE)) -> np.array:
    """
    Preprocess images by following steps:

    Args:
        image_path: Image path for preprocessing
        size: image size for resizing
    Returns:
        Processed images in numpy array data type
    """
    image = cv2.imread(image_path) # read image
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # convert image into RGB channel (OpenCV default BGR)
    resized_image = cv2.resize(image_rgb, size) # resize image to size+(3,)
    final_image = EFNetPreProcessInput(resized_image) # preprocess image by efficientNet preprocess input
    
    return final_image

def create_dataset(images:np.array, batch_size:int=32) -> tf.data.Dataset:
    """Create dataset from images."""
    image_ds = tf.data.Dataset.from_tensor_slices(tf.constant(images)) # generate image dataset
    image_ds = image_ds.batch(batch_size) # convert image dataset to 32 batch size
    image_ds = image_ds.prefetch(buffer_size=tf.data.AUTOTUNE)  # prefetch data for higher efficiency
    
    return image_ds

def calculate_accuracy(y_true:tf.Tensor, y_pred:tf.Tensor) -> np.float32:
    """
    Create accuracy score via true labels and model predictions.

    Args:
        y_true: True labels from dataset
        y_pred: Model predictions
    Returns:
        Accuracy score
    """
    results = tf.equal(tf.argmax(y_pred, axis=1), tf.argmax(y_true, axis=1))
    results_to_float = tf.cast(results, tf.float32)
    accuracy_score = tf.reduce_mean(results_to_float).numpy()

    return accuracy_score

def evaluate(class_indices:dict, real_classes:list, species_path:str, model:tf.keras.Model) -> float:
    """
    Evaluate model performance from test images collected before.

    Args:
        class_indices: Dictionary of class names and class indices
        real_classes: List of real classes
        species_path: Test images path
        model: Model for evaluation
    Returns:
        Accuracy score in float data type
    """
    # Prepare testing images and labels
    test_image_and_paths = [(img_path, class_indices[cls]) for cls in real_classes \
                                                           for img_path in Path(species_path).joinpath(cls).glob('*')]
    image_paths, labels = zip(*test_image_and_paths) # separate images and labels
    test_images = [preprocess_image(str(img_path), size=(IMG_SIZE, IMG_SIZE)) for img_path in image_paths] # prepare test images
    test_labels = tf.one_hot(labels, depth=len(np.unique(np.array(labels)))) # prepare test labels with one hot encoding
    test_dataset = create_dataset(test_images, batch_size=BATCH_SIZE) # create testing dataset by tensorflow
    y_preds = model.predict(test_dataset)
    Acc_Score = calculate_accuracy(test_labels, y_preds)

    return Acc_Score

def train_classifier(species:str='', save_model=False) -> AnimalClassifier:
    # Data preprocessing
    data_transformer = DataTransformer(ANNOTATION_PATH)
    data_df = data_transformer.preprocess()

    # Data augmentation
    if species.lower() == 'cats':
        df_species = data_df[data_df['SPECIES']==1] # cat : 1 --> epochs: 5, fine_tune_ratio=0.15, fine_tune_epochs=5
        params = {'epochs': 5, 'fine_tune_ratio': 0.15, 'fine_tune_epochs': 5, 'lr_decay_type': 'step'}
    elif species.lower() == 'dogs':
        df_species = data_df[data_df['SPECIES']==2] # dog : 2 --> epochs: 10, fine_tune_ratio=None, fine_tune_epochs=0
        params = {'epochs': 10, 'fine_tune_ratio': None, 'fine_tune_epochs': 0, 'lr_decay_type': None}
    else: raise ValueError('cats or dogs only !')
    
    data_aug = DataAugmentation(dataframe=df_species,
                                img_data_path=DATA_PATH, 
                                img_size=IMG_SIZE, 
                                batch_size=BATCH_SIZE, 
                                preprocess_function=EFNetPreProcessInput)
    train_data_gen, valid_data_gen = data_aug.create_flow()

    # prepare label classes
    class_indices = train_data_gen.class_indices
    real_classes = get_classes(class_indices, save_path=Path.cwd().joinpath('%s_classes.npy'%(species)))
    
    # Model training
    base_model = EfficientNetB0(include_top=False)
    breed_classifier = AnimalClassifier(base_model,  
                                        input_shape=INPUT_SHAPE, 
                                        output_shape=len(real_classes), 
                                        epochs=params['epochs'], 
                                        Init_lr=1e-3,
                                        fine_tune_ratio=params['fine_tune_ratio'], 
                                        fine_tune_epochs=params['fine_tune_epochs'], 
                                        lr_decay_type=params['lr_decay_type'])
    breed_classifier.train(train_data_gen, valid_data_gen)

    # Model saving
    if save_model: breed_classifier.model.save(Path.cwd().joinpath('%s_classifier.h5'%(species)))

    # Model evaluation
    species_path = Path(TEST_PATH).joinpath(species)
    acc_score = evaluate(class_indices, real_classes, species_path, breed_classifier.model)
    print(f"Accuracy score on testing dataset: {acc_score}")

    return breed_classifier

if __name__ == '__main__':
    # Set random seed and clear session
    seed = 42
    np.random.seed(seed)
    tf.random.set_seed(seed)
    tf.keras.backend.clear_session()
    cats_classifier = train_classifier('cats', save_model=True)
    dogs_classifier = train_classifier('dogs', save_model=True)