import tensorflow as tf
from pathlib import Path
from tqdm import tqdm
from animal_detector import AnimalDetector  # Ensure this module is correctly implemented

# Define directories
RAW_DATA_DIR = Path(
    "C:/Users/User/Desktop/Data_Science_Notebook/datasets/Cats_and_Dogs_Breeds_Classification_Oxford_Dataset/images/images"
)
CROPPED_DATA_DIR = Path("datasets/cropped_images/")
RAW_LIST_DIR = Path("datasets/annotations")

def process_and_save_images():
    """
    Processes images by detecting and cropping animals, then saves them.
    """
    detector = AnimalDetector()
    image_paths = list(RAW_DATA_DIR.glob("*.jpg"))  # Modify if using different formats
    
    for img_path in tqdm(image_paths, ncols=100):
        try:
            cropped_img = detector.detect(img_path)
            
            if cropped_img.size == 0:
                print(f"Skipping {img_path}, no object detected.")
                continue
            
            save_path = Path(CROPPED_DATA_DIR) / img_path.name
            tf.keras.preprocessing.image.save_img(str(save_path), cropped_img)
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

def create_train_val_test_list():
    train_val_list = RAW_LIST_DIR / "trainval.txt"
    test_list = RAW_LIST_DIR / "test.txt"
    target_train_val_list = RAW_LIST_DIR / "cropped_trainval.txt"
    target_test_list = RAW_LIST_DIR / "cropped_text.txt"
    origin_files = [train_val_list, test_list]
    target_files = [target_train_val_list, target_test_list]

    image_paths = [imgPath.name for imgPath in CROPPED_DATA_DIR.glob("*.jpg")]
    print(image_paths[:5])

    for idx, txt_file in enumerate(origin_files):
        with open(txt_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        target_path = target_files[idx]
        with open(target_path, 'w', encoding='utf-8') as file:
            for line in tqdm(lines, ncols=100):
                imgPath = line.strip().split(' ')[0]+'.jpg'
                if imgPath in image_paths:
                    file.write(line)


if __name__ == "__main__":
    process_and_save_images()
    create_train_val_test_list()
