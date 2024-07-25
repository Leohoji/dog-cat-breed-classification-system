import mysql.connector
from mysql_password import PASSWORD

# database connection and operations
class DatabaseManager:
    @staticmethod
    def connect(self):
        self.connection = mysql.connector.connect(host='localhost',
                                                  port='3306',
                                                  user='root',
                                                  password=PASSWORD)
        self.cursor = self.connection.cursor()

    @staticmethod
    def add_member(user_data):
        pass

    @staticmethod
    def get_animal_info(breed):
        pass

    @staticmethod
    def update_historical_data(user, animal, feedback=None):
        pass