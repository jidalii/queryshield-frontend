from dataclasses import dataclass

@dataclass
class UserRegistration():
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    password: str = ""
    role: str = ""
    
@dataclass
class UserLogin():
    email: str = ""
    password: str = ""