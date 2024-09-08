from model import DatabaseManager


class Verification:
    def __init__(self):
        self.mysql_connector = DatabaseManager()

    def login_verify(self, user_data:dict) -> str:
        """
        Verify user data from login interface.

        Args:
            user_data: Dictionary of user's information.
        Returns:
            String of 'user not exists', 'wrong password', or 'yes'.
        """
        # get member information
        member_info = self.mysql_connector.get_member_info(user_data)

        # check information
        if not member_info:
            result = 'user not exists'
        else:
            _, UserName, UserPassword, _ = member_info # (id, user_name, user_password, timestamp)
            result = (UserName, UserPassword)
            print(f"output: {result}")
            if member_info != UserPassword:
                result = 'wrong password' # password is incorrect
            else:
                result = 'yes'

        return result
    
    def sign_up_verify(self, user_data:dict) -> str:
        """
        Verify user data from sign_up interface.

        Args:
            user_data: Dictionary of user's information.
        Returns:
            String of 'success', or 'fail'.
        """
        # get member information
        member_info = self.mysql_connector.get_member_info(user_data)

        # check information
        if not member_info:
            user_name, user_password  = self.mysql_connector.get_user_info(user_data)
            self.mysql_connector.add_member(user_name, user_password)
            response = 'success'
        else: response = 'fail' 

        return response
    
    def collect_historical_data(self):
        pass

    def save_to_historical_data(self):
        pass

    def send_results(self):
        pass