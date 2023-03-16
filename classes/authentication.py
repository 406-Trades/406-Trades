# Login / Create Account Information Validation Class
class Authentication:
    def __init__(self, username, password, passwordTwo):
        self.username = username
        self.password = password
        self.passwordTwo = passwordTwo

    # Checks if user input into login page is valid
    def valid_login(self):
        if self.username and self.password:
            return True
    
    # Checks if user input into create account page is valid
    def valid_create(self):
        if self.username and self.password and (self.password == self.passwordTwo):
            return True