import requests
from bs4 import BeautifulSoup
import json
import sys
'''can scrap only public instagram accounts'''
class Instagram:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):   #constructor
        self.username = username
    def scrap(self):
        try:
            url = f"https://instagram.com/{self.username}"        
            respond = requests.get(url)             #requesting
            if respond.status_code == 404:          #if page not found
                print("Failed to connect or user does not exist!")
                exit()
            if respond.status_code == 200:          #if there is response
                soup = BeautifulSoup(respond.content,"html.parser")
                script_tag = soup.find("script",type = "application/ld+json")
                json_data = json.loads(str(script_tag.text.strip()))
                name = json_data['name']
                username = json_data['alternateName']
                description = json_data['description']
                URL = json_data['url']
                profile_image_link = json_data['image']
                return {
                 "name" : name,
                 "username" : username,
                 "description" : description,
                 "URL" : URL,
                 "image_link" : profile_image_link,   
                } 
        except Exception as ex:
            print(ex)            

insta = Instagram()
print(insta.scrap())    



