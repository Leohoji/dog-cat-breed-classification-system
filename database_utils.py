import mysql.connector
from mysql_password import HOST, PORT, USER, PASSWORD

# database connection and operations
class DatabaseManager:
    def connect(self):
        """
        Connect local MySQL database.
        """
        self.connection = mysql.connector.connect(host=HOST,
                                                  port=PORT,
                                                  user=USER,
                                                  password=PASSWORD)
        self.cursor = self.connection.cursor()
    
    def disconnect(self):
        """
        Disconnect local MySQL database.
        """
        self.cursor.close()
        self.connection.close()

    def login_verify(self, user_data:dict):
        """
        Verify user data from login interface.

        Args:
            user_data: Dictionary of user's information.
        Returns:
            String of 'user not exists', 'wrong info', or 'yes'.
        """
        pass

    def add_member(user_data):
        pass

    def get_animal_info(breed):
        pass

    def update_historical_data(user, animal, feedback=None):
        pass

if __name__ == '__main__':
    mysql_manager = DatabaseManager()
    mysql_manager.connect()
    print('ok')