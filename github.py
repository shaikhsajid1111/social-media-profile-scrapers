import requests
from bs4 import BeautifulSoup
import sys

class Github:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
    def scrap(self):
        try:
            URL = f'https://github.com/{self.username}'    
            response = requests.get(URL)
            if response.status_code == 404:
                print("User does not exist!")
                exit()
            if response.status_code == 200:
                soup = BeautifulSoup(response.content,'html.parser')

                full_name = soup.find("span",{
                    'class' : 'p-name vcard-fullname d-block overflow-hidden'
                }).text
                bio = soup.find('div',{
                    'class' : 'p-note user-profile-bio mb-2 js-user-profile-bio'
                }).text
                
                location = soup.find('span',{
                    'class' : 'p-label'
                }).text
                status = soup.find('div',{
                    'class' : 'user-status-message-wrapper'
                }).text
                
                email = soup.find('li',{
                    'itemprop' : 'email'
                }).text
                return {
                    'full_name' : full_name,
                    'bio' : bio,
                    'location' : location,
                    'status':  status
                                   }
        except Exception as ex:
            print(ex)   

usr = Github()
print(usr.scrap())            