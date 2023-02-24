from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')

s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service = s,options=chrome_options)
driver.maximize_window()

start_pages = 1
total_pages = 3

catalog_link_prefix = "https://sharegpt.com/explore/new?page="
for i in range(start_pages,total_pages):
    driver.get(catalog_link_prefix + str(i))
    print(catalog_link_prefix + str(i))
    time.sleep(3) 
  
    html = driver.page_source
    
    # Now, we could simply apply bs4 to html variable
    soup = BeautifulSoup(html, "html.parser")
    # driver.find_element(By.NAME, 'q').send_keys('Yasser Khalil')
    # Getting the title tag
    divs = soup.find_all('div', class_='grid gap-2 flex-1')
    for div in divs:
        conversation_link = div.find('a').get('href')
        print(conversation_link)
