import requests
from bs4 import BeautifulSoup
import sys

class Github:
    @staticmethod
    def scrap(username):
        try:
            URL = f'https://github.com/{username}'    
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

if __name__ == "__main__":
    print(Github.scrap(sys.argv[len(sys.argv)-1]))