import requests 
from bs4 import BeautifulSoup
import requests
import sys
from fake_headers import Headers
class Facebook():
    @staticmethod
    def scrap(username):
        try:
            URL = f"https://facebook.com/{username}"
            headers = Headers().generate()
            respond = requests.get(URL,headers = headers)
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


if __name__ == '__main__':
    print(Facebook.scrap(sys.argv[len(sys.argv)-1]))