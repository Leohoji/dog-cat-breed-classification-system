import mysql.connector
from mysql_info import DATABASE_NAME, HOST, PORT, USER, PASSWORD

# database connection and operations
class DatabaseManager:
    def __init__(self):
        self.get_user_info = lambda user_data: (user_data['user_name'], user_data['user_password'])

    def connect(self):
        """
        Connect local MySQL database.

        Returns: Cursor object of mysql.connector.
        """
        self.connection = mysql.connector.connect(host=HOST,
                                                  port=PORT,
                                                  user=USER,
                                                  password=PASSWORD,
                                                  database=DATABASE_NAME)
        self.cursor = self.connection.cursor()
        self.cursor.execute("SET SQL_SAFE_UPDATES = 0;")

        return self.cursor
    
    def disconnect(self):
        """
        Disconnect local MySQL database.
        """
        self.cursor.close()
        self.connection.commit()
        self.connection.close()

    def login_verify(self, user_data:dict) -> str:
        """
        Verify user data from login interface.

        Args:
            user_data: Dictionary of user's information.
        Returns:
            String of 'user not exists', 'wrong password', or 'yes'.
        """
        cursor = self.connect() # login database
        user_name, user_password = self.get_user_info(user_data) # get user data
        print(f"input: {(user_name, user_password)}")
        
        # query for collecting member info
        mem_info_record = self.get_member_info(cursor, user_name)

        # check information
        if not mem_info_record:
            result = 'user not exists'
        else:
            _, UserName, UserPassword, _ = mem_info_record
            result = (UserName, UserPassword)
            print(f"output: {result}")
            if user_password != UserPassword:
                result = 'wrong password' # password is incorrect
            else:
                result = 'yes'

        self.disconnect() # disconnect database
        return result

    def sign_up_verify(self, user_data:dict) -> str:
        """
        Verify user data from sign_up interface.

        Args:
            user_data: Dictionary of user's information.
        Returns:
            String of 'success', or 'fail'.
        """
        cursor = self.connect() # login database
        user_name, user_password = self.get_user_info(user_data) # get user data
        print(f"input: {(user_name, user_password)}")

        # query for collecting member info
        mem_info_record = self.get_member_info(cursor, user_name)

        # check information
        if not mem_info_record:
            self.add_member(cursor, user_name, user_password)
            response = 'success'
        else: response = 'fail'

        self.disconnect() # disconnect database
        return response
        
    def get_member_info(self, user_data:dict) -> list:
        """
        Get member information from MySQL database.

        Args:
            user_data: Dictionary of user's information.
        Returns:
            List of member information.
        """
        cursor = self.connect() # login database
        user_name = user_data['user_name'] # get user data
        query = f"SELECT * FROM `member_info` WHERE user_name = %(user_name)s;"
        cursor.execute(query, {'user_name': user_name})
        mem_info = cursor.fetchone()
        self.disconnect() # disconnect database

        return mem_info

    def add_member(self, cursor, user_name:str, user_password:str) -> str:
        """
        Add member information to MySQL database.

        Args:
            cursor: Cursor object of mysql.connector
            user_name: User's name for table insertion.
            user_password: User's password for table insertion.
        """
        query = f"INSERT INTO `member_info` (user_name, user_password) VALUES (%s, %s);"
        cursor.execute(query, (user_name, user_password))

    def get_animal_info(self, animal_breed:str) -> dict:
        """
        Get animal breed information from MySQL database.

        Args:
            animal_breed
        Returns:
            Animal breed information in dictionary data type.
        """
        cursor = self.connect() # login database
        query = f"SELECT * FROM `animal` WHERE animal_breed = %(animal_breed)s;"
        cursor.execute(query, {'animal_breed': animal_breed})
        animal_info = cursor.fetchone()
        print(animal_info)
        
        # create animal data
        keys = ('animal_id', 'animal_breed', 'image_1', 'image_2', 'image_3', 'animal_description')
        animal_data = {}
        for key, value in zip(keys, animal_info):
            animal_data[key] = value

        self.disconnect() # disconnect database
        return animal_data
    
    def get_historical_data(self, user_name:str) -> list:
        """
        Collect user's historical data from check data interface.

        Args:
            user_name: Member's user name
        Returns:
            List of historical data.
        """
        cursor = self.connect() # login database
        query = f"SELECT * FROM `user_history` WHERE user_name = %(user_name)s;"
        cursor.execute(query, {'user_name': user_name})
        historical_data = cursor.fetchall()
        for data in historical_data:
            print(f"Historical data: {data}")
        
        self.disconnect() # disconnect database
        return True

    def update_historical_data(self, user_name:str, image:bytes, feedback:str='') -> bool:
        """
        Update historical data for user's classification result into MySQL database.

        Args:
            user_name: Member's user name
            image: Image for classification
            feedback: If classification result by classifier is wrong, user will add feedback.
        Returns:
            True for success or False for failure.
        """
        cursor = self.connect() # login database
        results = feedback if feedback else 'yes'
        query = f"INSERT INTO `user_history` (user_name, image, results) VALUES (%s, %s, %s);"
        cursor.execute(query, (user_name, image, results))
        self.disconnect() # disconnect database
        return True

if __name__ == '__main__':
    import string
    import random
    def generate_fake_data(fake_name=''):
        if not fake_name:
            fake_name = ''.join(random.choices(string.ascii_letters, k=8)) + '@gmail.com'
        fake_password = ''.join(random.choices(string.ascii_letters, k=4)) + ''.join(random.choices('0123456789', k=4))
        
        return (fake_name, fake_password)
    
    def convert_image_to_blob(image_path='cat.jpg'):
        with open(image_path, 'rb') as file:
            return file.read()
    
    # test user data, first is all correct, second one's password is incorrect
    user_data_1 = {'user_name': '12345qwer@gmail.com', 'user_password': 'sdlkjfg455'}
    user_data_2 = {'user_name': '56789qwer@gmail.com', 'user_password': 'xxxxxxxxx'}
    user_data_3 = {'user_name': 'xxxxxxxxxx', 'user_password': 'xxxxxxxxx'}
    mysql_manager = DatabaseManager()
    for data in (user_data_1, user_data_2, user_data_3):
        result = mysql_manager.login_verify(data)
        print(result)
    
    # test sign up verification, first is random, second is 
    test_sign_up = False
    if test_sign_up:
        fake_user_name_1, fake_user_password_1 = generate_fake_data()
        print(f"Fake member 1: {(fake_user_name_1, fake_user_password_1)}")
        fake_user_name_2, fake_user_password_2 = generate_fake_data(fake_name=user_data_1['user_name'])
        print(f"Fake member 2: {(fake_user_name_2, fake_user_password_2)}")
        fake_data_1 = {'user_name': fake_user_name_1, 'user_password': fake_user_password_1}
        fake_data_2 = {'user_name': fake_user_name_2, 'user_password': fake_user_password_2}

        for data in (fake_data_1, fake_data_2):
            response = mysql_manager.sign_up_verify(data)
            print(response)
    
    # Test for getting historical data
    mysql_manager.get_historical_data(user_name=user_data_1['user_name'])

    # Test for getting animal data
    animal_data = mysql_manager.get_animal_info(animal_breed='Labrador')
    print(animal_data)

    # Test for updating historical data
    update_result = mysql_manager.update_historical_data(user_name=user_data_1['user_name'], image=None)
    print(update_result)