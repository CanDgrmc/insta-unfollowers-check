from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
from bs4 import BeautifulSoup as bs
import urllib.parse

class Follower:
    def __init__(self, email, password):
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        self.browser = webdriver.Chrome(desired_capabilities=caps,executable_path='.\chromedriver.exe')
        self.email = email
        self.password = password

    def signIn(self):
        self.browser.get('https://www.instagram.com/accounts/login/')
        time.sleep(1)
        emailInput = self.browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[2]/div/label/input')
        passwordInput = self.browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input')

        emailInput.send_keys(self.email)
        passwordInput.send_keys(self.password)
        passwordInput.send_keys(Keys.ENTER)
        time.sleep(2)
        self.browser.find_element_by_xpath('/html/body/div[4]/div/div/div[3]/button[2]').click()

    def process_browser_log_entry(self, entry):
        response = json.loads(entry['message'])['message']
        return response
    def saveFollowers(self):
        profileButton = self.browser.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[3]/a')
        profileButton.click()
        time.sleep(4)
        followersButton = self.browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a')
        followersButton.click()

        time.sleep(1)
        browser_log = self.browser.get_log('performance')
        events = [self.process_browser_log_entry(entry) for entry in browser_log]
        events = [event for event in events if 'Network.response' in event['method']]

        for event in events:
            if event.get('params') is None:
                continue
            if event['params'].get('response') is None:
                continue
            if event['params']['response']['headers'].get('content-type') is None:
                continue
            if "json" in event['params']['response']['headers']['content-type']:

                if "fetch_mutual" in event['params']['response']['url']:
                    people = []
                    hasNextPage = dict['data']['user']['edge_followed_by']
                    while hasNextPage:
                        endCursor = ''
                        url = urllib.parse.unquote(event['params']['response']['url'])
                        baseUrl = url[:95]
                        j = json.loads(str(url[95:]))
                        print(j)
                        j['first'] = 48
                        j['after'] = endCursor
                        newUrl = baseUrl + json.dumps(j)
                        self.browser.get(newUrl)
                        soup = bs(self.browser.page_source, 'html.parser')
                        dict = json.loads(soup.find("body").text)
                        for el in dict['data']['user']['edge_followed_by']['edges']:
                            people.append(el['node']['username'])
                        hasNextPage = dict['data']['user']['edge_followed_by']['page_info']['has_next_page']
                        endCursor = dict['data']['user']['edge_followed_by']['page_info']['end_cursor']
                        ## todo  recursive requests



                    with open('people.json', 'w') as my_data_file:
                        my_data_file.write(json.dumps(people))
                        my_data_file.close()
        print('Followers: %s', format(len(people)))
        print('####################')
        self.browser.close()

        return

    ## todo  recursive requests


instance = Follower('email/phone','password')
instance.signIn()
instance.saveFollowers()