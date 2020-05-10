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
            headers = {'user-agent' : 'Your User Agent'}
            '''
            tiktok server can stop responding if too much request happens, so try modifying requests.get() with below given code:
                - requests.get(URL,headers = headers,proxies={"http": "http://111.233.225.166:1234"})
                                or
                - requests.get(URL,headers = headers,verify = False)
                                or
                - requests.get(URL,headers = headers,timeout = 5)                

            '''
            respond = requests.get(URL,headers = headers,proxies={"http": "http://111.233.225.166:1234"})
            if respond.status_code == 404:
                print("Failed to connect or user does not exist!")
                exit()
            if respond.status_code == 200:
                soup =  BeautifulSoup(respond.content,"html.parser")
    
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
user = Tiktok('username goes here')   #or pass username  from command line    
print(user.scrap())                
