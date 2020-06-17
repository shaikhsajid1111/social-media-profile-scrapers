import requests
from bs4 import BeautifulSoup
import sys
from fake_headers import Headers
class Reddit:
    @staticmethod
    def scrap(username):
        try:
            url = f"https://reddit.com/user/{username}"   
            headers = Headers().generate()     
            respond = requests.get(url,headers = headers)             #requesting
            if respond.status_code == 404:          #if page not found
                print("Failed to connect or user does not exist!")
                exit()
            if respond.status_code == 200:
                soup = BeautifulSoup(respond.content,"html.parser")
                
                bio = soup.find("div",{
                    "class" : "bVfceI5F_twrnRcVO1328"
                }).text.strip()
                
                banners = soup.find("div",{
                    "class" : "_39u8lkB0jifV2dCyGxhTst"
                })
                
                profile = soup.find("img",{
                    "class" : "_2TN8dEgAQbSyKntWpSPYM7 M_wdt3XN_OW7h8RYbg38W"
                })
                
                karma = soup.find("span",{
                    "id" : "profile--id-card--highlight-tooltip--karma"
                }).text.strip()
                
                birth_date = soup.find("span",{
                    "id" : "profile--id-card--highlight-tooltip--cakeday"
                }).text.strip()
                
            
                return {
                    "bio" : bio,
                    "banner" : banners['style'].split("(")[1].split("?")[0] if banners is not None else "Banner Not Found!",
                    "profile_image" : profile['src'].split("?")[0] if profile is not None else "Profile Image Not Found!",
                    "karma" : karma,
                    "birth_date" : birth_date
                }
        except Exception as ex:
             print(ex)        
    
       

if __name__ == '__main__':
    print(Reddit.scrap(sys.argv[len(sys.argv)-1]))