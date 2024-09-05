import time
import urllib
from pathlib import Path
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AnimalImageCrawler:
    """
    AnimalImageCrawler class object can crawl cats or dogs images, 
    
    Args:
        service: The local address of webdriver.exe for selenium module.
        breed_list: List of animal breeds for searching.
        species: Species for "cats" or "dogs".
    """
    def __init__(self, service_path:str, breed_list:list, species:str):
        self.service_path = service_path
        self.animal_breeds = breed_list
        self.create_dir_if_not_exist = lambda path: Path.mkdir(path, parents=True, exist_ok=True)\
                                                    if not Path.is_dir(path)\
                                                    else None
        # Limit the content of animal parameter
        if species.lower()=='cats' or species.lower()=='dogs':
            self.species = species.lower()
        else:
            raise ValueError('cats or dogs only!')
        
        # Create target directory
        self.target_dir = Path(Path.cwd()).joinpath('test_images', self.species)
        self.create_dir_if_not_exist(self.target_dir)
        
        # Target address for crawling
        self.URL = 'https://www.google.com.tw/images'

    def set_headers(self):
        """Set headers before using webdriver server."""
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
    
    def crawling_from_google_images(self, image_number:int=10):
        """
        Crawl several animal images from chrome server, and save them.
    
        Args:
            image_number: The number of images you want to crawl.
        """
        self.set_headers()
        for breed in self.animal_breeds:
            service = Service(executable_path=self.service_path)
            driver = webdriver.Chrome(service=service)
            driver.get(self.URL)
            
            # Find the search bar and search keyword
            keyword = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            keyword.clear()
            print(f"Searching {breed} ...")
            keyword.send_keys('%s %s all images' % (breed, self.species))
            keyword.send_keys(Keys.RETURN)
            
            # Collect image src
            counts = 1
            image_srcs = []
            self.img_dir = Path(self.target_dir).joinpath(breed)
            self.create_dir_if_not_exist(self.img_dir)
            while counts < image_number: 
                try:
                    images = WebDriverWait(driver, 5).until( # Find images
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".F0uyec"))
                    )
                except: 
                    images = WebDriverWait(driver, 5).until( # Find images
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".fR600b"))
                    ) 
                for image in images:
                    src = image.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    if src in image_srcs: continue # Check unique path
                    image_srcs.append(src)
        
                    # Check whether save the right src
                    if isinstance(src, str):
                        save_to = Path(self.img_dir).joinpath(breed + '_' + str(counts) + '.jpg')
                        urlretrieve(src, save_to) # Save images
                        counts += 1
                    else: pass
                print(f"Download {counts} images...")
                
                # Scroll Down Webpage
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(3)
                try:
                    # Input button: "show more results" button
                    more_results = driver.find_element(By.CLASS_NAME, 'LZ4I')
                    # "Looks like you've reached the end" hint
                    end = driver.find_element(By.CLASS_NAME, 'Yu2Dnd').find_element(By.TAG_NAME, 'div').text 
                    # If mouse scroll to bottom, break.
                    if end:
                        print("Looks like you've reached the end !!!!!")
                        break
                    more_results.click()
                    time.sleep(3) # wait for loading
                except:
                    pass

            print(f"{breed} Finish, total images: {len(image_srcs)}")
            driver.close()
        print("All images have been downloaded, YAA!!!!!!!!")        


if __name__ == '__main__':
    dog_classes = ['american bulldog', 'american pit bull terrier', 'basset hound',
                   'beagle', 'boxer', 'chihuahua', 'english cocker spaniel',
                   'english setter', 'german shorthaired', 'great pyrenees',
                   'havanese', 'japanese chin', 'keeshond', 'leonberger',
                   'miniature pinscher', 'newfoundland', 'pomeranian', 'pug',
                   'saint bernard', 'samoyed', 'scottish terrier', 'shiba inu',
                   'staffordshire bull terrier', 'wheaten terrier', 'yorkshire terrier']
    cat_classes = ['Abyssinian', 'Bengal', 'Birman', 'Bombay', 'British Shorthair',
                   'Egyptian Mau', 'Maine Coon', 'Persian', 'Ragdoll', 'Russian Blue',
                   'Siamese', 'Sphynx']
    driver_path = 'C:\\Users\\User\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe'
    
    for species, breed_list in (('dogs', dog_classes), ('cats', cat_classes)):
        image_crawler = AnimalImageCrawler(service_path=driver_path, 
                                           breed_list=breed_list, 
                                           species=species)
        image_crawler.crawling_from_google_images()