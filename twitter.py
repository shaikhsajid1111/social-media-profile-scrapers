import requests
from bs4 import BeautifulSoup
import sys
from fake_headers import Headers
class Twitter:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
    def scrap(self):
        try:
            #generating URL according to the username
            url = f"https://twitter.com/{self.username}"

            #making response 
            respond = requests.get(url,headers = Headers().generate())
            if respond.status_code == 404:          #page not found
                print("Failed to connect or user does not exist!")
                exit()
            if respond.status_code == 200:    
                soup = BeautifulSoup(respond.content,"html.parser")
            #profile image
                profile_image_link = soup.find("img",{
            "class" : "css-9pa8cd",
        })
                full_name = soup.find('span',{
            "class" : 'css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0'
        })    
                is_verified = soup.find("span",{
           "class" : "ProfileHeaderCard-badges"
       })
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
                media_count = soup.find("a",{
            "class" :"PhotoRail-headingWithCount"
        })
      
                return {
            "profile_image" : profile_image_link['src'],
            "full_name" : full_name.text.strip(),
   
            "account_verified" : True if is_verified is not None else False,
            "bio" : bio.text.strip(),
            "joined_date" : joined_date.text.strip(),
            "birth_date" : birth_date.text.strip(),
            "location" : location.text.strip(),
            "tweets_count" : tweets,
            "following" : following,
            "followers" : followers,
            "website" : website['title'] if website is not None else "Not Found!",    
            "media_count" : media_count.text.strip()
        }
        except Exception as ex:
            print(ex)   
             
twiter_bot = Twitter("shaikhsajid1111")  #can pass username here or from command line
print(twiter_bot.scrap())


'''
need to update as per the twitter website update
'''