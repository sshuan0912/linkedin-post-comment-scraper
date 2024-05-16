
# This project is aimed to scrape Linkedin post comments and commentor profiles, including name, position and profile url
# Programming lanugage is Python. Selenium library is used for automating web browsers. BeautifulSoup is for scraping text from HTML
# User is able to input a Linkedin post link, then this link is validated automatically.
# After validation, user needs to type their email and password to login their Linkedin account
# Comments data is stored into a cvs file if there's comment in this post

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import re
import time
from getpass import getpass
import csv

# set up web driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Linkedin Post Link URL validation
def is_link_validated(url):
    valid = bool(re.match(r'https://www.linkedin.com/posts/[\w-]+', url))
    return valid

# Login Linkedin by entering email and password
def login(url):

    driver.get(url)
    time.sleep(5)  # Wait for login page loading

    email = input("Enter your email: ")
    password = getpass()
    email_input = driver.find_element(By.ID, 'username')
    email_input.send_keys(email)
    password_input = driver.find_element(By.ID, 'password')
    password_input.send_keys(password)

    # click button to log in
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()

    time.sleep(5)  # wait for login 

# check if current webpage have more comments to display
def check_more_comments():
    try:
        return bool(driver.find_element(By.CLASS_NAME,'comments-comments-list__load-more-comments-button'))
    except:
        return False

# main funtion
def scrape_comments(url):
    # check link validation; if link is invalid, raise an error
    if not is_link_validated(url):
        raise ValueError("Invalid LinkedIn post URL.")
    
    # nagivate to login webpage and call login() to log in
    login('https://www.linkedin.com/login')

    # Go to the post webpage we want to get comments info
    driver.get(url)
    time.sleep(5)  # wait for page loading

    # Scroll to load all comments
    # As long as there is "check more comments" button at the bottom, we need to click it and load more comments till there's no button
    while(check_more_comments()):

        # scroll to the bottom of current page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # locate "check more comments" button and click it to get additional comments
        show_more_button = driver.find_element(By.CLASS_NAME,'comments-comments-list__load-more-comments-button')
        show_more_button.click()

        # wait for more comments loading
        time.sleep(3)

    # scroll to bottom if no additional comments
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    src = driver.page_source  
    driver.quit()

    # scrape comments info
    # Extract the HTML content and parse with Beautiful Soup
    soup = BeautifulSoup(src, "html.parser")

    # locate comments, iterate each comment to extract data and write data into CVS file
    # if there's no comment in this post, handle exception
    try: 
        # locate comments
        comments = soup.find_all("article", class_="comments-comment-item")
        if len(comments) == 0:
            print("No Comments in this Linkedin post!!!")
            return
        
        # csv file field names
        fields = ['name', 'profile_url', 'position', 'comment_text']

        # name of csv file
        filename = "linkedin_post_comments.csv"

        # writing to csv file
        with open(filename, 'w') as csvfile:

            # creating a csv dict writer object
            writer = csv.DictWriter(csvfile, fieldnames=fields)
 
            # writing headers (field names)
            writer.writeheader()

            # iterate each comment to extract data
            for comment in comments:
                try:
                    name_tag = comment.find(attrs={"aria-hidden": "true"})
                    name = name_tag.get_text(strip=True)
                    position = comment.find('span', class_='comments-post-meta__headline').get_text(strip=True)
                    profile_url = comment.find("a", class_="comments-post-meta__actor-link")['href']
                    comment_text = comment.find("div", class_="comments-comment-item__inline-show-more-text").get_text(strip=True)

                    # create dictionary for each record
                    comment_dict = {'name':name, 'profile_url':profile_url, 'position':position, 'comment_text':comment_text}

                    # use code below to print out result
                    # print(f"Name: {name}\nProfile URL: {profile_url}\nCurrent Position: {title}\nComment: {comment_text}\n")

                    # writing data into file
                    writer.writerow(comment_dict)

                except Exception as E:
                    print(E)

    except Exception as E:
        print(E)


# input a valid linkedin post link to start this program
url = input("Enter the Linkedin post link: ")
scrape_comments(url)

