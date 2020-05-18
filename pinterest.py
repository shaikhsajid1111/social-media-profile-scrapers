import requests
import sys
from bs4 import BeautifulSoup
import json
from random import choice

class Pinterest:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
    def get_proxy(self):
        url = "https://www.sslproxies.org"
        req = requests.get(url)

        soup = BeautifulSoup(req.content, 'html.parser')
    
        proxy_list = []
        for proxy in soup.find_all('td'):
            proxy_list.append(proxy.text)

        ip = proxy_list[0::8]
        port = proxy_list[1::8]

        proxies = []
        for i in range(0, len(ip)):
            for j in range(0, len(ip)):
                if i == j:
                    proxies.append(":".join([ip[i], port[j]]))
        chosen_proxy = choice(proxies)
        return{'http': f'http://{chosen_proxy}',
                'https' : f'https://{chosen_proxy}',
                'ftp' : f'ftp://{chosen_proxy}'
        }    
    def scrap(self):
        URL = f'https://in.pinterest.com/{self.username}/'
        response = requests.get(URL,proxies= {"http": "http://111.233.225.166:1234"})    
        if response.status_code == 404:
            print("User does not exist!")
            exit()
        if response.status_code == 200:
            soup = BeautifulSoup(response.content,'html.parser')    
            #print(soup.prettify())
            script_tag = soup.find('script',{
                'id' : 'initial-state'
            })
            #print(type(script_tag))
            json_data = json.loads(str(script_tag.text.strip()))
            #print(json_data.keys())
            #print(json_data['resourceResponses'])
            data = json_data['resourceResponses'][0]['response']['data']
            user_data = data['user']
            #print(user_data.keys())
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

user = Pinterest()
print(user.scrap())            