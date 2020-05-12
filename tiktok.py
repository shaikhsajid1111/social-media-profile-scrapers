import requests
from bs4 import BeautifulSoup
import sys
import json
class Tiktok:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
    def scrap(self):
        try:
            URL = f'https://tiktok.com/@{self.username}'
            print(URL)
            #headers = {'user-agent' : 'Your User Agent'}
            
            response = requests.get(URL)
            if response.status_code == 404:
                print("Failed to connect or user does not exist!")
                exit()
            if response.status_code == 200:
            
                soup =  BeautifulSoup(response.content,"html.parser")
                print(soup.prettify())
                script_tag = soup.find(
                    'script',{
                        'id' : '__NEXT_DATA__'
                    })
                
                json_data = json.loads(str(script_tag.text.strip()))
                
                #dict_keys(['props', 'page', 'query', 'buildId', 'assetPrefix', 'isFallback', 'customServer'])
                user_data = json_data['props']['pageProps']['userData']
                sec_id = user_data['secUid']
                user_id = user_data['userId']
                is_secret = user_data['isSecret']
                unique_name = user_data['uniqueId']
                signature = user_data['signature']
                covers = user_data['coversMedium']
                following = user_data['following']
                fans = user_data['fans']
                heart = user_data['heart']
                video = user_data['video']
                is_verified = user_data['verified']
                return {
                    'sec_id' : sec_id,
                    'user_id' : user_id,
                    'is_secret' : is_secret,
                    'username' : unique_name,
                    'bio' : signature,
                    'cover_image' : covers,
                    'following' : following,
                    'fans' : fans,
                    'hearts' : heart,
                    'video' : video,
                    'is_verified' : is_verified,
                }

        except Exception as ex:
            print(ex)        
user = Tiktok()   #or pass username  from command line    
print(user.scrap())                
