from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import time
from bs4 import BeautifulSoup

class Linkedin:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
    def scrap(self):
        url = f'https://in.linkedin.com/in/{self.username}?trk=public_profile_browsemap_profile-result-card_result-card_full-click'
        
        #automating and opening URL in headless browser
        chrome_option = Options()
        chrome_option.add_argument('--headless')            
        chrome_option.add_argument('--disable-extensions')
        chrome_option.add_argument('--disable-gpu')
        chrome_option.add_argument('--incognito')
        driver = webdriver.Chrome('C:\\webdrivers\\chromedriver.exe',options=chrome_option) #chromedriver's path in first argument
        driver.get(url)
        time.sleep(5)
        response = driver.page_source.encode('utf-8').strip()
            
        soup =  BeautifulSoup(response,'html.parser')    
        full_name = soup.find('h1',{
            'class' : 'top-card-layout__title'
        })
        profession = soup.find('h2',{
            'class' : 'top-card-layout__headline'
        })
        address = soup.find('span',{
            'class' : 'top-card__subline-item'
        })
        connections = soup.find('span',{
            'class' : 'top-card__subline-item top-card__subline-item--bullet'
        })
        educations = soup.find_all('span',{
            'class' : 'top-card-link__description'
        })
        websites = soup.find_all('span',{
            'class' : 'websites__url-text'
        })
        summary = soup.find('section',{
            'class' : 'summary pp-section'
        })
        experience = soup.find_all('li',{
            'class' : 'experience-item'
        })
        experience = [experience[i].text.strip().replace('\n','') for i in range(len(experience))]
        websites = [websites[i].text.strip() for i in range(len(websites))]
        educations = [educations[i].text.strip() for i in range(len(educations)-1)]
        education_list = soup.find_all('span',{
            'class' : 'education__item education__item--degree-info'
        })
        education_list = [education_list[i].text.strip() for i in range(len(education_list))]
        skills_list = soup.find_all('li',{
            'class' : 'skills__item'
        })
        skills_list = [skills_list[i].text.strip() for i in range(len(skills_list))]
        honors = soup.find('p',{
            'class' : 'show-more-less-text__text--more'
        })
        
        return {
            'full_name' : full_name.text.strip(),
            'profession': profession.text.strip() if type(profession) is not None else 'Not found',
            'address' : address.text.strip() if type(address) is not None else 'Not found',
            'connections' : connections.text.strip(),
            'university' : educations,
            'websites' : websites if type(websites) is not None else 'Not found',
            'experience' : experience,
            'degrees' : education_list,
            'skills' : skills_list,
            'honors' : honors if type(honors) is not None else 'Not found!',
            'summary' : summary.text.strip() if type(summary) is not None else 'Not found',
        }
        
user = Linkedin()
print(user.scrap())             