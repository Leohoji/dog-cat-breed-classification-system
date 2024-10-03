import traceback
import mysql.connector
from mysql_info import DATABASE_NAME, HOST, PORT, USER, PASSWORD

# database connection and operations
class DatabaseManager:
    def __init__(self):
        self.get_user_info = lambda user_data: (user_data['user_name'], user_data['user_password'])

    def connect(self) -> bool:
        """
        Connect local MySQL database.

        Returns: Cursor object of mysql.connector.
        """
        try:
            self.connection = mysql.connector.connect(host=HOST, port=PORT,
                                                      user=USER, password=PASSWORD,
                                                      database=DATABASE_NAME, 
                                                      auth_plugin='mysql_native_password')
            self.cursor = self.connection.cursor()
            self.cursor.execute("SET SQL_SAFE_UPDATES = 0;")

        except: traceback.print_exc()
    
    def disconnect(self):
        """
        Disconnect local MySQL database.
        """
        self.cursor.close()
        self.connection.commit()
        self.connection.close()
        
    def get_member_info(self, user_data:dict) -> list:
        """
        Get member information from MySQL database.

        Args:
            user_data: Dictionary of user's information.
        Returns:
            List of member information.
        """
        self.connect() # login database
        user_name = user_data.get('user_name') # get user data
        query = f"SELECT * FROM `member_info` WHERE user_name = %(user_name)s;"
        self.cursor.execute(query, {'user_name': user_name})
        mem_info = self.cursor.fetchone()
        self.disconnect() # disconnect database

        return mem_info

    def add_member(self, user_name:str, user_password:str) -> str:
        """
        Add member information to MySQL database.

        Args:
            cursor: Cursor object of mysql.connector
            user_name: User's name for table insertion.
            user_password: User's password for table insertion.
        """
        self.connect() # login database
        query = f"INSERT INTO `member_info` (user_name, user_password) VALUES (%s, %s);"
        self.cursor.execute(query, (user_name, user_password))
        self.disconnect() # disconnect database
        print(f"Successfully add {user_name} and {user_password} into `member_info` table.")

    def get_animal_info(self, animal_breed:str) -> dict:
        """
        Get animal breed information from MySQL database.

        Args:
            animal_breed
        Returns:
            Animal breed information in dictionary data type.
        """
        self.connect() # login database
        query = f"SELECT * FROM `animal` WHERE animal_breed = %(animal_breed)s;"
        self.cursor.execute(query, {'animal_breed': animal_breed})
        animal_info = self.cursor.fetchone()
        
        # create animal data
        keys = ('animal_id', 'animal_breed', 'image_1', 'image_2', 'animal_description', 'animal_link')
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
        self.connect() # login database
        query = f"SELECT * FROM `user_history` WHERE user_name = %(user_name)s;"
        self.cursor.execute(query, {'user_name': user_name})
        historical_data = self.cursor.fetchall()
        self.disconnect() # disconnect database

        return historical_data

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
        self.connect() # login database
        results = feedback if feedback else 'yes'
        query = f"INSERT INTO `user_history` (user_name, image, results) VALUES (%s, %s, %s);"
        self.cursor.execute(query, (user_name, image, results))
        self.disconnect() # disconnect database
        return True

if __name__ == '__main__':
    import string
    import random
    def generate_fake_data(fake_name=''):
        if not fake_name:
            fake_name = ''.join(random.choices(string.ascii_letters, k=8)) + '@gmail.com'
        fake_password = ''.join(random.choices(string.ascii_letters, k=4)) + ''.join(random.choices('0123456789', k=4))
        
        return {'user_name': fake_name, 'user_password': fake_password}
    
    # test user data, first is all correct, second one's password is incorrect
    user_data_1 = {'user_name': '12345qwer@gmail.com', 'user_password': 'sdlkjfg455'}
    user_data_2 = {'user_name': '56789qwer@gmail.com', 'user_password': 'xxxxxxxxx'}
    user_data_3 = generate_fake_data()
    print(f"Fake member info: {(user_data_3['user_name'], user_data_3['user_password'])}")
    mysql_manager = DatabaseManager()
    for data in (user_data_1, user_data_2, user_data_3):
        result = mysql_manager.get_member_info(data)
        print(result)
    
    # Test for getting historical data
    res = mysql_manager.get_historical_data(user_name=user_data_1['user_name'])
    print(f"historical data \n {res}")

    # Test for getting animal data
    animal_data = mysql_manager.get_animal_info(animal_breed='Labrador')
    print(animal_data)

    # Test for updating historical data
    # update_result = mysql_manager.update_historical_data(user_name=user_data_1['user_name'], image=None)
    # print(update_result)