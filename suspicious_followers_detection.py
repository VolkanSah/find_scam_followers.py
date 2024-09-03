import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def random_sleep(min_time=1, max_time=3):
    time.sleep(random.uniform(min_time, max_time))

def login(driver, username, password):
    driver.get('https://www.instagram.com/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
    
    username_input = driver.find_element(By.NAME, 'username')
    username_input.send_keys(username)
    random_sleep()
    password_input = driver.find_element(By.NAME, 'password')
    password_input.send_keys(password)
    random_sleep()
    password_input.send_keys(Keys.ENTER)
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/inbox/')]")))

def get_followers(driver, username, max_followers=None):
    driver.get(f'https://www.instagram.com/{username}/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/followers/")]')))
    
    followers_button = driver.find_element(By.XPATH, '//a[contains(@href, "/followers/")]')
    followers_button.click()
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"] ul div li')))
    
    follower_elements = []
    last_height = driver.execute_script("return arguments[0].scrollHeight", driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"] > div:nth-child(2)'))
    
    while True:
        follower_elements = driver.find_elements(By.CSS_SELECTOR, 'div[role="dialog"] ul div li')
        
        if max_followers and len(follower_elements) >= max_followers:
            break
        
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"] > div:nth-child(2)'))
        random_sleep(0.5, 1.5)
        
        new_height = driver.execute_script("return arguments[0].scrollHeight", driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"] > div:nth-child(2)'))
        if new_height == last_height:
            break
        last_height = new_height
    
    return follower_elements[:max_followers] if max_followers else follower_elements

def is_suspicious(username, bio, suspicious_keywords):
    return any(keyword in username.lower() for keyword in suspicious_keywords) or \
           any(keyword in bio.lower() for keyword in suspicious_keywords)

def analyze_followers(driver, follower_elements, suspicious_keywords):
    suspicious_followers = []
    
    for elem in follower_elements:
        try:
            user_link = elem.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            username = user_link.split('/')[-2]
            
            driver.get(user_link)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'main')))
            
            try:
                bio_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.-vDIg > span')))
                bio = bio_element.text
            except TimeoutException:
                bio = ""
            
            if is_suspicious(username, bio, suspicious_keywords):
                user_id = user_link.split('/')[-2]
                suspicious_followers.append((username, user_id))
            
        except (NoSuchElementException, TimeoutException):
            print(f"Couldn't analyze follower: {username}")
        
        random_sleep(1, 3)  # Variiere die Wartezeit zwischen Profilaufrufen
    
    return suspicious_followers

def main():
    username = 'your_username'
    password = 'your_password'
    max_followers_to_check = 1000  # Begrenzen Sie die Anzahl der zu überprüfenden Follower
    
    suspicious_keywords = ['spam', 'bot', 'fake', 'scam', 'contest', 'followforfollow', 'lfl', 'meme',
                           'spamsquishy', 'instagood', 'mood', 'dankmemes', 'memesdaily', 'share', 'followback',
                           'twitter', 'gaintrick', 'cute', 'slime', 'scammers', 'scammer', 'twitterquotes',
                           'scammersofinstagram', 'selfie', 'polishgirl', 'edits', 'scammeralert', 'relatable',
                           'likeforlikeback', 'spams', 'twittermemes', 'followtrain', 'views', 'spammers',
                           'dubaixd', 'dubaixxd', 'dubai', 'youlikehits', 'socialexchange', 'youhavewon', 'win',
                           'onlyfans', 'manyvid', 'f4f', 's4s', 'l4l', 'follow4follow', 'like4like',
                           'spamforspam', 'spam4spam', 'shoutout4shoutout', 'fakeaccount', 'fakefollowers',
                           'getfollowers', 'getlikes']
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        login(driver, username, password)
        random_sleep(2, 4)  # Warte nach dem Login
        follower_elements = get_followers(driver, username, max_followers_to_check)
        suspicious_followers = analyze_followers(driver, follower_elements, suspicious_keywords)
        
        with open('suspicious_followers.txt', 'w') as f:
            for follower in suspicious_followers:
                f.write(f'{follower[0]} ({follower[1]})\n')
        
        print(f"Analyse abgeschlossen. {len(suspicious_followers)} verdächtige Follower gefunden.")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
