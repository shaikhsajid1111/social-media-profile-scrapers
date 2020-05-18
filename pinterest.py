import requests
import sys
from bs4 import BeautifulSoup
import json
from proxies import get_proxy

class Pinterest:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
      
    def scrap(self):
        try:
            URL = f'https://in.pinterest.com/{self.username}/'
            proxy = get_proxy()
            proxies = {
            'http' : f'http://{proxy}',
            'https' : f'https://{proxy}',
            'ftp' : f'ftp://{proxy}'
        }
        
            response = requests.get(URL,proxies= proxies)    
            if response.status_code == 404:
                print("User does not exist!")
                exit()
            if response.status_code == 200:
                soup = BeautifulSoup(response.content,'html.parser')    
            
                script_tag = soup.find('script',{
                'id' : 'initial-state'
            })
            
                json_data = json.loads(str(script_tag.text.strip()))
            
                data = json_data['resourceResponses'][0]['response']['data']
                user_data = data['user']
            
                is_verified_merchant = user_data['is_verified_merchant']
                full_name = user_data['full_name']
                impressum_url = user_data['impressum_url']
                pin_count = user_data['pin_count']
                domain_url = user_data['domain_url']
                profile_image = user_data['image_xlarge_url']
                bio = user_data['about']
                board_count = user_data['board_count']
                is_indexed = user_data['indexed']
                follower = user_data['follower_count']
                following = user_data['following_count']
                country = user_data['country']
                location = user_data['location']
            
                return{
                'full_name' : full_name,
                'profile_image' : profile_image,
                'followers' : follower,
                'followings' : following,
                'bio' : bio,
                'country' : country,
                'impressum_url' : impressum_url,
                'website' : domain_url,
                'board_count' : board_count,
                'location' : location,
                'pin_count' : pin_count,
                'is_verified' : is_verified_merchant,

            }
        except Exception as ex:
            print(ex)    

user = Pinterest()
print(user.scrap())            