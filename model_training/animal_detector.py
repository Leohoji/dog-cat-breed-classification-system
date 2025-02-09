import tensorflow as tf
import tensorflow_hub as hub

class AnimalDetector:
    def __init__(self):
        self.module_handle = "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1" 
        self.object_detector = hub.load(self.module_handle).signatures['default']
        print("Object detector loading...")
    
    def load_img(self, path):
        """Load image via tensorflow io API"""
        img = tf.io.read_file(path)
        img = tf.image.decode_jpeg(img, channels=3)
        return img
    
    def detect(self, img_path):
        img = self.load_img(str(img_path))

        # detector inference
        converted_img  = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
        result = self.object_detector(converted_img)
        ymin, xmin, ymax, xmax = result["detection_boxes"][0].numpy()

        img_np = img.numpy()
        height, width, _ = img_np.shape
        ymin = int(ymin * height)
        ymax = int(ymax * height)
        xmin = int(xmin * width)
        xmax = int(xmax * width)
        cropped_img = img_np[ymin:ymax, xmin:xmax]

        return cropped_img
