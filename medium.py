import requests
from bs4 import BeautifulSoup
import sys

class Medium:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
    def scrap(self):
        try:
            url = f"https://medium.com/@{self.username}"
            
            headers = {'user-agent' : 'Your User Agent'}
            
            respond = requests.get(url)
            if respond.status_code == 404:
                print("Failed to connect or user does not exist!")
                exit()
            if respond.status_code == 200:    
                soup = BeautifulSoup(respond.content,"html.parser")
    
                #user have paid membership
                full_name = soup.find('h1',{
                    'class' :  'av q dp cj dq ck dr ds dt y'
                     
                })
                is_paid_member = True
                bio = soup.find('p',{
                    'class' : 'eq er cj b ck es et cn y'
                })
                subtitle = soup.find_all('a',{
                    'class' :'cd ce bm bn bo bp bq br bs bt ex bw bx ch ci'
                })
                extra_info = [subtitle[i].text for i in range(5) if len(subtitle) > 0]
                
                if full_name and bio and subtitle is not None:
                    return {
                        'full_name' : full_name.text,
                        'is_paid_member' : is_paid_member,
                        'bio' : bio.text,
                        'extras' : extra_info,
                       
                    }    
        except Exception as ex:
            print(ex)
        #if free account
        else:
            full_name = soup.find('h1',{
                'class' : 'av q dh cj di ck dj dk dl y'
            })      
            is_paid_member = False
            bio = soup.find('p',{
                'class' : 'ei ej cj b ck ek el cn y'
            })
            subtitle = soup.find_all('a',{
                'class' : 'cd ce bm bn bo bp bq br bs bt eo bw bx ch ci'
            })
            extra_info = [subtitle[i].text for i in range(5) if len(subtitle) > 0]
            if full_name and bio is not None:              
                return {
                        'full_name' : full_name.text,
                        'is_paid_member' : is_paid_member,
                        'bio' : bio.text,
                        'extras' : extra_info
                    }
med = Medium()
print(med.scrap())            