import requests
from bs4 import BeautifulSoup
import sys

class Twitter:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
    def scrap(self):
        try:
            url = f"https://twitter.com/{self.username}"
        
            respond = requests.get(url)
            if respond.status_code == 404:
                print("Failed to connect or user does not exist!")
                exit()
            if respond.status_code == 200:    
                soup = BeautifulSoup(respond.content,"html.parser")
            #profile image
                profile_image_link = soup.find("img",{
            "class" : "ProfileAvatar-image",
        })
                full_name = soup.find('a',{
            "class" : 'fullname'
        })
                username = soup.find('b',{
            "class" : "u-linkComplex-target"
        })
                is_verified = soup.find("span",{
           "class" : "ProfileHeaderCard-badges"
       })
                if is_verified is None:
                    is_verified = False
                else:
                    is_verified = True
                bio = soup.find("p",{
            "class" : "ProfileHeaderCard-bio"
        })  
                joined_date = soup.find("span",{
            "class" : "ProfileHeaderCard-joinDateText"
        })
                birth_date = soup.find("span",{
            "class" : "ProfileHeaderCard-birthdateText"
        })
                location = soup.find("span",{
            "class" : "ProfileHeaderCard-locationText"
        })
                followings_followers = [span.get('data-count') for span in soup.findAll("span",{"class":"ProfileNav-value"})]
        
                tweets = followings_followers[0]
                following = followings_followers[1]
                followers = followings_followers[2]
        
                website = soup.find("span",{
            "class" : "ProfileHeaderCard-urlText"
        }).find("a",{
            "class" : "u-textUserColor"
        })
                if website is not None:
                    website = website['title']
                else:
                    website = None    
        
                media_count = soup.find("a",{
            "class" :"PhotoRail-headingWithCount"
        })
      
                return {
            "profile_image" : profile_image_link['src'],
            "full_name" : full_name.text.strip(),
            "username" : username.text.strip(),
            "account_verified" : is_verified,
            "bio" : bio.text.strip(),
            "joined_date" : joined_date.text.strip(),
            "birth_date" : birth_date.text.strip(),
            "location" : location.text.strip(),
            "tweets_count" : tweets,
            "following" : following,
            "followers" : followers,
            "website" : website,    
            "media_count" : media_count.text.strip()
        }
        except Exception as ex:
            print(ex)   
             
twiter_bot = Twitter()  #can pass username here or from command line
print(twiter_bot.scrap())
