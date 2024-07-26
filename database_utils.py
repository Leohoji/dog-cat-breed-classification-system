import mysql.connector
from mysql_info import DATABASE_NAME, HOST, PORT, USER, PASSWORD

# database connection and operations
class DatabaseManager:
    def __init__(self):
        self.get_user_info = lambda user_data: (user_data['user_name'], user_data['user_password'])

    def connect(self):
        """
        Connect local MySQL database.
        """
        self.connection = mysql.connector.connect(host=HOST,
                                                  port=PORT,
                                                  user=USER,
                                                  password=PASSWORD,
                                                  database=DATABASE_NAME)
        self.cursor = self.connection.cursor()
        self.cursor.execute("SET SQL_SAFE_UPDATES = 0;")
    
    def disconnect(self):
        """
        Disconnect local MySQL database.
        """
        self.cursor.close()
        self.connection.close()

    def login_verify(self, user_data:dict) -> str:
        """
        Verify user data from login interface.

        Args:
            user_data: Dictionary of user's information.
        Returns:
            String of 'user not exists', 'wrong password', or 'yes'.
        """
        self.connect() # login database
        user_name, user_password = self.get_user_info(user_data) # get user data
        print(f"input: {(user_name, user_password)}")
        
        # query for collecting member info
        mem_info_record = self.get_member_info(self.cursor, user_name)

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
        self.connect() # login database
        user_name, user_password = self.get_user_info(user_data) # get user data
        print(f"input: {(user_name, user_password)}")

        # query for collecting member info
        mem_info_record = self.get_member_info(self.cursor, user_name)

        # check information
        if not mem_info_record:
            self.add_member(user_name, user_password)
            response = 'success'
        else: response = 'fail'

        self.disconnect() # disconnect database
        return response
        
    def get_member_info(self, cursor, user_name:str) -> list:
        """
        Get member information from MySQL database.

        Args:
            cursor: Cursor object of mysql.connector
            user_name: Member's user name
        Returns:
            List of member information.
        """
        query = f"SELECT * FROM `member_info` WHERE user_name = %(user_name)s;"
        cursor.execute(query, {'user_name': user_name})
        mem_info_record = cursor.fetchone()

        return mem_info_record

    def add_member(self, user_name, user_password):
        pass

    def get_animal_info(breed):
        pass

    def update_historical_data(user, animal, feedback=None):
        pass

if __name__ == '__main__':
    # test user data, first is all correct, second one's password is incorrect
    user_data_1 = {'user_name': '12345qwer@gmail.com', 'user_password': 'sdlkjfg455'}
    user_data_2 = {'user_name': '56789qwer@gmail.com', 'user_password': 'xxxxxxxxx'}
    user_data_3 = {'user_name': 'xxxxxxxxxx', 'user_password': 'xxxxxxxxx'}
    mysql_manager = DatabaseManager()
    for data in (user_data_1, user_data_2, user_data_3):
        result = mysql_manager.login_verify(data)
        print(result)