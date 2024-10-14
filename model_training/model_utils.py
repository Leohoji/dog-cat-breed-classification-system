import cv2
import math
import pandas as pd
import numpy as np
import tensorflow as tf
from functools import partial
from pathlib import Path
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.efficientnet import preprocess_input as EFNetPreProcessInput

IMG_SIZE = 224
BATCH_SIZE = 32

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
    
class AnimalClassifier:
    def __init__(self, base_model, input_shape, output_shape, epochs=5, Init_lr=1e-3,
                 fine_tune_ratio=None, fine_tune_epochs=3, lr_decay_type:str=''):
        """
        Args:
          base_model: Transfer learning model passed into building structure.
          input_shape: Input shape for the transfer model.
          output_shape: Output shape for the transfer model.
          epochs: Epochs for model training.
          fine_tune_ratio: Ratio for trainable layers of base model.
          fine_tune_epochs: Epochs for model fine-tuning.
          lr_decay_type: Type of learning rate decay
        """
        self.base_model       = base_model
        self.input_shape      = input_shape
        self.output_shape     = output_shape
        self.epochs           = epochs
        self.fine_tune_ratio  = fine_tune_ratio
        self.fine_tune_epochs = fine_tune_epochs
        self.Epoch            = self.epochs + self.fine_tune_epochs

        # ----------------------------
        # Model optimization
        # 1. learning rate scheduler
        # 2. learning rate decay
        # ----------------------------
        self.Init_lr           = Init_lr
        self.Adam              = tf.keras.optimizers.Adam
        self.compile_model     = lambda model, lr=self.Init_lr: model.compile(loss='categorical_crossentropy', 
                                                                              optimizer=self.Adam(learning_rate=lr), 
                                                                              metrics=['accuracy'])
        self.early_stopping    = tf.keras.callbacks.EarlyStopping(monitor='val_loss', mode='min', patience=3, 
                                                                  verbose=2, restore_best_weights=True)
        if lr_decay_type:
            self.lr_decay_type = lr_decay_type
            self.Min_lr        = self.Init_lr * 0.001
            self.lr_func       = self.get_lr_scheduler(lr_decay_type=self.lr_decay_type, 
                                                       lr=self.Init_lr, 
                                                       min_lr=self.Min_lr, 
                                                       total_iters=self.Epoch)
            self.lr_scheduler  = tf.keras.callbacks.LearningRateScheduler(self.lr_func, verbose=1)
            self.callbacks     = [self.lr_scheduler]
        else:
            self.reduce_lr     = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.8, patience=1, 
                                                                      verbose=2, min_lr=self.Init_lr * 0.0001, mode='min')
            self.callbacks     = [self.reduce_lr]

    def build_model(self):
        """Build a transfer learning model."""
        self.base_model.trainable = False
    
        inputs = tf.keras.layers.Input(shape=self.input_shape, name="input_layer")
        x = self.base_model(inputs, training=False)
        x = tf.keras.layers.GlobalAveragePooling2D(name="global_average_pooling_layer")(x)
        outputs = tf.keras.layers.Dense(self.output_shape, activation="softmax", name="output_layer")(x)
        model = tf.keras.Model(inputs, outputs, name="animal_classifier")
    
        print(model.summary())
    
        return model

    def get_lr_scheduler(self, lr_decay_type:str, lr:float, min_lr:float, total_iters:int,
                         warmup_iters_ratio:float=0.1, warmup_lr_ratio:float=0.1, no_aug_iter_ratio:float=0.3, step_num:int=10):
        """
        Functions for learning rate decay, cosine or step decay.
    
        Args:
            lr_decay_type: Type of learning rate decay, cos or step
            lr: Learning rate
            min_lr: Minimum learning rate
            total_iters: Total iterations of training
            warmup_iters_ratio: Ratio for warm up iteration
            warmup_lr_ratio: Ratio for warm up learning rate
            no_aug_iter_ratio: Ratio for no augmentation iterations, this phase will maintain at minimum learning rate.
            step_num: Number of steps for step decay
        Returns:
            Function for learning rate decay.
        """
        def yolox_warm_cos_lr(lr, min_lr, total_iters, warmup_total_iters, warmup_lr_start, no_aug_iter, iters):
            if iters <= warmup_total_iters: # warm up iters
                lr = (lr - warmup_lr_start) * pow(iters / float(warmup_total_iters), 2) + warmup_lr_start
            elif iters >= total_iters - no_aug_iter: # no augmentation iters, it will maintain at minimum iter
                lr = min_lr
            else: # learning rate decay
                lr = min_lr + 0.5 * \
                    (lr - min_lr) * \
                    (1.0 + math.cos(math.pi * (iters - warmup_total_iters) / (total_iters - warmup_total_iters - no_aug_iter)))
            return lr

        def step_lr(lr, decay_rate, step_size, iters):
            if step_size < 1:
                raise ValueError("step_size must above 1.")
            n       = iters // step_size # Number of steps
            out_lr  = lr * decay_rate ** n # learning rate decay
            return out_lr
        
        if lr_decay_type == "cos":
            warmup_total_iters  = min(max(warmup_iters_ratio * total_iters, 1), 3) # range [1, 3]
            warmup_lr_start     = max(warmup_lr_ratio * lr, 1e-3) # at least 1e-3
            no_aug_iter         = min(max(no_aug_iter_ratio * total_iters, 1), 3) # range [1, 5]
            func = partial(yolox_warm_cos_lr ,lr, min_lr, total_iters, warmup_total_iters, warmup_lr_start, no_aug_iter)
        else:
            decay_rate          = (min_lr / lr) ** (1 / (step_num - 1)) # decay rate
            step_size           = total_iters / step_num
            func                = partial(step_lr, lr, decay_rate, step_size)

        return func

    def train(self, train_data, valid_data):
        self.model = self.build_model()
        self.compile_model(self.model, lr=self.Init_lr)
        self.original_history = self.model.fit(train_data, 
                                               epochs=self.epochs,
                                               validation_data=valid_data,
                                               callbacks=[self.callbacks],
                                               initial_epoch=0)
        if self.fine_tune_ratio:
            self.fine_tune_model_layers()
            self.compile_model(self.model, lr=self.Init_lr * 0.1)
            self.new_history = self.model.fit(train_data, 
                                              epochs=self.epochs+self.fine_tune_epochs,
                                              validation_data=valid_data,
                                              callbacks=[self.callbacks],
                                              initial_epoch=self.epochs)
        else: 
            pass

    def fine_tune_model_layers(self):
        """Set specific layers being trainable for further model training."""
        fine_tune_base_model = self.model.layers[1]
        layer_number = -int(len(fine_tune_base_model.layers) * self.fine_tune_ratio)
    
        # Unfreeze all of the layers in the base model
        fine_tune_base_model.trainable = True
    
        # Refreeze every layer except for the last 5
        for layer in fine_tune_base_model.layers[:layer_number]:
            layer.trainable = False
    
        print(f"Change last {-layer_number} layers of {fine_tune_base_model.name} successfully, please recompile model again.")


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