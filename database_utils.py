import mysql.connector
from mysql_password import HOST, PORT, USER, PASSWORD

# database connection and operations
class DatabaseManager:
    @staticmethod
    def connect(self):
        """
        Connect local MySQL database.
        """
        self.connection = mysql.connector.connect(host=HOST,
                                                  port=PORT,
                                                  user=USER,
                                                  password=PASSWORD)
        self.cursor = self.connection.cursor()
    
    @staticmethod
    def disconnect(self):
        """
        Disconnect local MySQL database.
        """
        self.cursor.close()
        self.connection.close()

    @staticmethod
    def login_verify(self, user_data:dict):
        pass

    @staticmethod
    def add_member(user_data):
        pass

    @staticmethod
    def get_animal_info(breed):
        pass

    @staticmethod
    def update_historical_data(user, animal, feedback=None):
        pass

if __name__ == '__main__':
    DatabaseManager.connect()
    print('ok')