import base64
import traceback
import numpy as np
from io import BytesIO
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont, ImageColor

import tensorflow as tf
import tensorflow_hub as hub 
from tensorflow.keras.models import load_model
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D


class AnimalDetector:
    def __init__(self, detector):
        # ---------------------------------------------------------------------------------------------------
        # Object detection model URL
        # MobileNetV2: "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1"
        # Inception_ResNetV2: "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1"
        # ---------------------------------------------------------------------------------------------------
        # self.module_handle = "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1" 
        # self.detector = hub.load(self.module_handle).signatures['default']
        self.detector = detector
        self.convert_float_to_int = lambda *args: (int(arg) for arg in args)

    def draw_bounding_box_on_image(self, image,
                                   ymin, xmin, ymax, xmax,
                                   color, font, thickness=4,
                                   display_str_list=()):
        """Adds a bounding box to an image."""
        draw = ImageDraw.Draw(image)
        im_width, im_height = image.size
        (left, right, top, bottom) = (xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height)
        draw.line([(left, top), (left, bottom), (right, bottom), (right, top), (left, top)],
                width=thickness,
                fill=color)

        display_str_heights = [font.getbbox(ds)[3] for ds in display_str_list]
        total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

        if top > total_display_str_height:
            text_bottom = top
        else:
            text_bottom = top + total_display_str_height

        for display_str in display_str_list[::-1]:
            bbox = font.getbbox(display_str)
            text_width, text_height = bbox[2], bbox[3]
            margin = np.ceil(0.05 * text_height)
            draw.rectangle([(left, text_bottom - text_height - 2 * margin), (left + text_width, text_bottom)], 
                           fill=color)
            draw.text((left + margin, text_bottom - text_height - margin),
                      display_str, fill="black", font=font)
            text_bottom -= text_height - 2 * margin
        
        return (left, right, top, bottom)

    def draw_one_boxes(self, image, boxes, class_names, scores):
        """Overlay labeled boxes on an image with formatted scores and label names."""
        colors = list(ImageColor.colormap.values())
        font = ImageFont.load_default()
        
        ymin, xmin, ymax, xmax = tuple(boxes)
        display_str = "{}: {}%".format(class_names.decode("ascii"), int(100 * scores))
        color = colors[hash(class_names) % len(colors)]
        
        image_pil = Image.fromarray(np.uint8(image)).convert("RGB")
        
        bbox = self.draw_bounding_box_on_image(image_pil, 
                                               ymin, xmin, ymax, xmax,
                                               color, font,
                                               display_str_list=[display_str])
        left, right, top, bottom = self.convert_float_to_int(*bbox)
        
        # Crop the image
        cropped_image_pil = image[top:bottom, left:right]
        cropped_image = np.array(cropped_image_pil)
        
        return image_pil, cropped_image

    def run_detector_one_img(self, img):
        # Detector inference
        converted_img  = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
        result = self.detector(converted_img)
        result = {key: value.numpy() for key, value in result.items()}

        # Draw result
        image_with_boxes, cropped_image = self.draw_one_boxes(img.numpy(), 
                                                              result["detection_boxes"][0],
                                                              result["detection_class_entities"][0], 
                                                              result["detection_scores"][0])

        object_class = result["detection_class_entities"][0].decode('utf-8')
        
        return (object_class, image_with_boxes, cropped_image)
    
class AnimalClassifier(tf.keras.Model):
    """MobileNetV2-based classifier for animal classification."""
    
    def __init__(self, 
                 input_feature: Tuple[int], output_dimension: int, model_name: str = 'animal_classifier'):
        """
        Create a transfer learning model based on MobileNetV2 for animal classification.

        Parameters:
            input_feature (List[int]): Shape of the input image (height, width, channels).
            output_dimension (int): Number of output classes.
            model_name (str): Name of the model (optional).
        """
        super(AnimalClassifier, self).__init__(name=model_name)

        self.input_feature = input_feature
        self.output_dimension = output_dimension

        # Define the model
        self.model = tf.keras.Sequential([
            MobileNet(input_shape=self.input_feature, include_top=False),  
            Dense(64, activation="relu", name="dense_layer", kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            Dropout(0.4),
            Dense(32, activation="relu", name="dense_layer_2", kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            Dropout(0.2),
            Dense(16, activation="relu", name="dense_layer_3", kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            Dropout(0.1),
            Dense(8, activation="relu", name="dense_layer_4", kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            Dropout(0.1),
            GlobalAveragePooling2D(name="global_average_pooling_layer"),
            Dense(output_dimension, activation="softmax", name="output_layer")
        ])
        
        self.model.layers[0].trainable = False  # Freeze the pre-trained weights

    def call(self, inputs, training=False, mask=None):
        """Forward pass of the model."""
        return self.model.call(inputs, training, mask)
    
class Classification:
    def __init__(self, classifier, label_path, img_size, ob_detector):
        self.detector = AnimalDetector(detector=ob_detector)
        self.classifier = classifier
        self.label_data = np.load(label_path, allow_pickle=True)
        self.img_size = img_size
        self.image_with_boxes = None
        self.cropped_image = None

    def decode_base64_image(self, base64_image_string:str) -> np.array:
        """Decode the base64 string and return the image as a PIL object"""
        try:
            base64_image_string = base64_image_string.split(",")[-1]
        except:
            base64_image_string = base64_image_string
        img_data = base64.b64decode(base64_image_string) # Decode the base64 string back to bytes
        self.img_array = tf.image.decode_jpeg(img_data, channels=3)
        return self.img_array
    
    def numpy_array_to_base64_image(self, array):
        """
        Convert a NumPy array to a Base64 encoded image string.

        Parameters:
        array (numpy.ndarray): The input NumPy array representing the image.

        Returns:
        str: Base64 encoded image string that can be used in an <img> tag.
        """
        # Ensure the array is in the correct format (uint8)
        if array.dtype != np.uint8:
            array = array.astype(np.uint8)
        
        # Convert NumPy array to a PIL Image
        image = Image.fromarray(array)

        # Save the image to a BytesIO object
        buffered = BytesIO()
        image.save(buffered, format="JPEG")  # You can change the format if needed
        base64_data = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Create the HTML <img> tag with Base64 data
        return base64_data

    def class_predict(self, base64_image_string:str) -> str:
        """Predict image after preprocessing and return predicted class"""
        image_rgb = self.decode_base64_image(base64_image_string)
        
        # Object detection
        object_class, img_with_bbox, cropped_img = self.detector.run_detector_one_img(image_rgb)
        real_classes = self.label_data['cats'] if object_class == "Cat" else self.label_data['dogs']
        self.image_with_boxes = self.numpy_array_to_base64_image(np.array(img_with_bbox))
        self.cropped_image = self.numpy_array_to_base64_image(cropped_img)

        # Image preprocessing
        image = tf.image.convert_image_dtype(cropped_img, tf.float32)
        image_for_pred = tf.image.resize(image, size=[self.img_size, self.img_size])[tf.newaxis, ...]
        
        # Model prediction
        model_pred = self.classifier(image_for_pred) # predict image
        pred_index = np.argmax(np.squeeze(model_pred)) # get the highest class index
        final_class = real_classes[pred_index] # final image class
        
        return object_class, final_class

    def send_results(self, base64_image_string:str) -> dict:
        """Send model prediction results to front-end in JSON data type."""
        try:
            object_class, final_pred = self.class_predict(base64_image_string)
            results = { 'status': 'ok', 'object_class': object_class, 'model_pred': final_pred }
        except Exception as E:
            traceback.print_exc()
            results = { 'status': 'error', 'msg': E.__class__.__name__ }

        return results
    
    def get_images(self):
        return self.image_with_boxes, self.cropped_image
    
    def get_label_data(self):
        return self.label_data
    
def custom_loss_fn(y_true, y_pred):
    loss_fn = CategoricalCrossentropy()
    loss = loss_fn(y_true, y_pred)

    return loss

def load_animal_classifier(model_path: str, label_path: str, img_size: int, ob_detector: tf.keras.Model) -> Classification:
    model_loaded = load_model(
        model_path, 
        custom_objects={
            'AnimalClassifier': AnimalClassifier, 
            'custom_loss_fn': custom_loss_fn
        }
    )
    return Classification(model_loaded, label_path, img_size=img_size, ob_detector=ob_detector)