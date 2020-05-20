import requests 
from bs4 import BeautifulSoup
import requests
import sys
class Facebook():
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username 
    def scrap(self):
        try:
            URL = f"https://facebook.com/{self.username}"
            respond = requests.get(URL)
            if respond.status_code == 404:
                print("Could Not Connect or User does not exist!\n")
            if respond.status_code == 200:
                soup = BeautifulSoup(respond.content,"html.parser")
                facebook_name = soup.find("span",{
                    "id":"fb-timeline-cover-name"
                })
                profile_image = soup.find("img",{
                    "class" : "_11kf img"
                })
                current_city = soup.find("li",{
                    "id" : "current_city"
                })
                clg = soup.find("div",{
                    "class" : "_2lzr _50f5 _50f7"
                })
               
                return {
                    "profile_image" : profile_image['src'],
                    "current_city" : current_city.text.strip(),
                    "Education" : clg.text.strip()
                }
        except Exception as ex:
             print(ex)       

fb = Facebook("shaikhsajid1111")
print(fb.scrap())        