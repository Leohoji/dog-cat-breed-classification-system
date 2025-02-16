import os
import time
import tempfile
import base64
import numpy as np
import tensorflow as tf
from io import BytesIO
from PIL import Image
from django.test import SimpleTestCase
from unittest.mock import patch
from model_loader import Classification

class DummyAnimalDetector:
    def __init__(self, detector):
        self.detector = detector

    def run_detector_one_img(self, image):
        """
        Simulate object detection by always returning "Cat" along with two dummy images.
        Here, we return a numpy array filled with a constant value (shape: (100, 100, 3)).
        """
        dummy_img = np.full(shape=(100, 100, 3), fill_value=128, dtype=np.uint8)
        return 'Cat', dummy_img, dummy_img

def dummy_classifier(x):
    """
    Define a dummy classifier that always returns a TensorFlow tensor,
    ensuring that np.argmax will return an index of 2 (corresponding to label_data['cats'][1], e.g., "Bengal").
    """
    # Assume the model outputs prediction probabilities for 3 classes,
    # and we force the second class to have a higher probability.
    return tf.constant([0.1, 0.7, 0.2])

class ClassificationTestCase(SimpleTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a temporary file and store fake label data (e.g., cat and dog breeds)
        cls.temp_label_file = tempfile.NamedTemporaryFile(delete=False, suffix='.npz')
        cls.label_file_path = cls.temp_label_file.name
        label_data = {"cats": np.array(["Abyssinian", "Bengal", "Birman"]), 
                      "dogs": np.array(["american bulldog", "american pit bull terrier", "basset hound"])}
        np.savez(cls.temp_label_file, **label_data)  # Save as NPZ format
        cls.temp_label_file.close()
        
        # Set up dummy parameters
        cls.img_size = 224
        cls.dummy_ob_detector = "dummy_detector_parameter"

        # Patch the AnimalDetector in model_loader with DummyAnimalDetector
        cls.animal_detector_patcher = patch(target="model_loader.AnimalDetector", new=DummyAnimalDetector)
        cls.animal_detector_patcher.start()

        # Create an instance of Classification
        cls.classification_instance = Classification(
            classifier=dummy_classifier,
            label_path=cls.label_file_path,
            img_size=cls.img_size,
            ob_detector=cls.dummy_ob_detector
        )

    @classmethod
    def tearDownClass(cls):
        cls.animal_detector_patcher.stop()

        # Make sure the Classification instance is cleaned up
        if hasattr(cls, 'classification_instance'):
            del cls.classification_instance
        
        # Try to delete the temporary file with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if os.path.exists(cls.label_file_path):
                    os.unlink(cls.label_file_path)
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(0.1)  # Wait a bit before retrying
                else:
                    print(f"Warning: Unable to delete {cls.label_file_path} after {max_retries} attempts")
        super().tearDownClass()
    
    def create_dummy_base64_image(self):
        """
        Generate a simple JPEG image (with a red background) and convert it to a Base64 encoded string.
        The prefix "data:image/jpeg;base64," simulates the format used by the frontend.
        """
        img = Image.new(mode="RGB", size=(200, 200), color=(255, 0, 0))
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        base64_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_str}"
    
    def test_decode_base64_image(self):
        base64_img = self.create_dummy_base64_image()
        img_tensor = self.classification_instance.decode_base64_image(base64_image_string=base64_img)

        # Verify that the returned object is a TensorFlow tensor and that its last dimension is 3 (RGB)
        self.assertIsInstance(img_tensor, tf.Tensor)
        self.assertEqual(img_tensor.shape[-1], 3)

    def test_to_numpy_array_to_base64_image(self):
        # Create a dummy numpy array representing an image
        dummy_array = np.full((100, 100, 3), 128, dtype=np.uint8)
        base64_result = self.classification_instance.numpy_array_to_base64_image(dummy_array)
        self.assertIsInstance(base64_result, str)

        # Try decoding the base64 string back to a PIL Image and verify its mode and size
        image_data = base64.b64decode(base64_result)
        image = Image.open(BytesIO(image_data))
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (100, 100))

    def test_class_predict(self):
        base64_img = self.create_dummy_base64_image()
        object_class, final_class = self.classification_instance.class_predict(base64_image_string=base64_img)

        # Since DummyAnimalDetector always returns "Cat" and dummy_classifier forces np.argmax to return 1,
        # the expected final prediction should be label_data['cats'][1], i.e., "Bengal"
        self.assertEqual(object_class, "Cat")
        self.assertEqual(final_class, "Bengal")
    
    def test_send_results(self):
        base64_img = self.create_dummy_base64_image()
        results = self.classification_instance.send_results(base64_image_string=base64_img)

        # Check the returned JSON data format and content
        self.assertEqual(results.get("status"), "ok")
        self.assertEqual(results.get("object_class"), "Cat")
        self.assertEqual(results.get("model_pred"), "Bengal")

