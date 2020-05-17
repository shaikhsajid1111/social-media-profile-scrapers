import requests
import sys
from bs4 import BeautifulSoup

class Pinterest:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
    def scrap(self):
        URL = f'https://in.pinterest.com/{self.username}/'
        response = requests.get(URL)    
        if response.status_code == 404:
            print("User does not exist!")
            exit()
        if response.status_code == 200:
            soup = BeautifulSoup(response.content,'html.parser')    
            print(soup.prettify())
user = Pinterest()
print(user.scrap())            