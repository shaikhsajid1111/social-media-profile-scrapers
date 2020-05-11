import requests
from bs4 import BeautifulSoup
import sys
import re

class Medium:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
    def scrap(self):
        try:
            url = f"https://medium.com/@{self.username}"
            #print(url)
            headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
            
            respond = requests.get(url,headers = headers,proxies={"http": "http://111.233.225.166:1234"})
            if respond.status_code == 404:
                print("Failed to connect or user does not exist!")
                exit()
            if respond.status_code == 200:    
                soup = BeautifulSoup(respond.content,"html.parser")
                #print(soup.prettify())
                #user have paid membership
                username = soup.find('h1',{
                    'class' :  'av q dp cj dq ck dr ds dt y'
                    #'av q dh cj di ck dj dk dl y' 
                })
                
                #print(image)
                if username is not None:
                    print(username.text)
        
        except Exception as ex:
            print(ex)
        #if free account
        else:
            username = soup.find('h1',{
                'class' : 'av q dh cj di ck dj dk dl y'
            })      
            if username is not None:              
                print(username.text)
med = Medium()
print(med.scrap())            