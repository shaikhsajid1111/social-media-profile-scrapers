import requests
import sys
from bs4 import BeautifulSoup

class Quora:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username

    def scrap(self):
        try:
            URL = f'https://quora.com/profile/{self.username}'
            print(URL)
            #headers = {'user-agent' : 'Your User Agent'}
            
            response = requests.get(URL)
            if response.status_code == 404:
                print("Failed to connect or user does not exist!")
                exit()
            if response.status_code == 200:   
                soup = BeautifulSoup(response.content,'html.parser')
                #print(soup.prettify())
                
        except Exception as ex:
            print(ex)        
usr = Quora('Kashish-Arora-60')
print(usr.scrap())                