# Login / Create Account Information Validation Class
import re
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
            if self.valid_user() and self.valid_pass(): 
                return True
    #Checks if it is a valid email address
    def valid_user(self):
        if re.match(r"[^@]+@[^@]+\.[^@]+", self.username):
            return True
    #Checks using regular expressions for at least 1 uppercase, lowercase, and number
    def valid_pass(self):
        if re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$", self.password):
            return True
    #For editing old password
    def new_pass(newPass):
        if  re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$", newPass):
            return True
        
    def new_user(username):
        if re.match(r"[^@]+@[^@]+\.[^@]+", username):
            return True