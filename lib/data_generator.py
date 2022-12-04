from datetime import datetime


class DataGenerator():

    def __init__(self):
        base_part = "learnqa"
        domain = "example.com"
        random_part = datetime.now().strftime("%m%d%Y%H%M%S")
        self.email = f"{base_part}{random_part}@{domain}"
        self.username = "learnqa"

    def generate_data(self, email=None, username=None):
        keys = ['password', 'username', 'firstName', 'lastName', 'email']
        values = ['123', f'{self.username if not username else username}', 'learnqa', 'learnqa',
                  f'{self.email if not email else email}']

        return {key: value for key, value in zip(keys, values)}
