import requests
from bs4 import BeautifulSoup
import sys
from fake_headers import Headers

class Medium:
    @staticmethod    
    def scrap(username):
        try:
            url = f"https://medium.com/@{username}"
            
            headers = Headers().generate()
            
            respond = requests.get(url,headers = headers)
            if respond.status_code == 404:
                print("Failed to connect or user does not exist!")
                exit()
            if respond.status_code == 200:    
                soup = BeautifulSoup(respond.content,"html.parser")
                
                #user have paid membership
                full_name = soup.find('h1',{
                    'class' :  'av q do ci dp cj dq dr ds y'
                     
                })
                is_paid_member = True
                bio = soup.find('p',{
                    'class' : 'ep eq ci b cj er es cm y'
                })
                subtitle = soup.find_all('a',{
                    'class' :'cc cd bm bn bo bp bq br bs bt ew bw cg ch'
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
                'class' : 'av q dg ci dh cj di dj dk y'
            })      
            is_paid_member = False
            bio = soup.find('p',{
                'class' : 'eh ei ci b cj ej ek cm y'
            })
            subtitle = soup.find_all('a',{
                'class' : 'cc cd bm bn bo bp bq br bs bt eo bw cg ch'
            })
            extra_info = [subtitle[i].text for i in range(5) if len(subtitle) > 0]
            if full_name and bio is not None:              
                return {
                        'full_name' : full_name.text,
                        'is_paid_member' : is_paid_member,
                        'bio' : bio.text,
                        'extras' : extra_info
                    }




if __name__ == '__main__':
    print(Medium.scrap(sys.argv[ len(sys.argv)-1] ))           
'''
last modified on : 16th June,2020
'''