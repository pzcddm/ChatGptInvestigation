'''
This python script is to web scrape the website(https://sharegpt.com/) and save each shared conversation between users and chatgpt
The website have multiple pages and in each page, there is a list of conversations.
The list of conversations have each conversation's url

The html format of conversation is:
    questions are wrapped into a p of class "pb-2"
    each question is followed by an answer and is wrapped into a div. But the paragraphs in a div are divided into p and li.
    it means each para

Then we gonna iterate each conversation and save it into our output path

Before accessing and saving a conversation, we need to define its format of our saved files.
The format of saving files is based on json:
    outermost layer is a list containing jsons,
    the format of each json:
        url: the url of this conversation in sharegpt server
        num: indicates how many conversations
        Q: An array storing the questions of conversation
        A: An array storing the answers of conversation

'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import json
import time
import os

def getAllIdsOfAHtml(soup):
    """
    get all tags which have a attribute 'id' from a BeautifulSoup and then output those numeric as a list

   :param BeautifulSoup soup: the BeautifulSoup from a website
   :return: a list that contains all the numeric id attribute (each id is actually a string that represents number)
   :rtype: list
   """
    tags = soup.find_all()
    ids = []
    for tag in tags:
        if 'id' in tag.attrs and tag['id'].isnumeric():
            ids.append(tag['id'])
    return ids

def extractConversationFrom(conversation_website):
    """
    Extract the conversation from the website in the sharegpt

   :param str conversation_website: the link of that website
   :return: a json dict that contains the content of the questions and answers
   :rtype: json dict
   """
    
    def getAllQA(soup, ids):
        questions = []
        answers = []
        for i, id in enumerate(ids):
            text_content = soup.find("div", {"id": id}).text
            if i % 2 == 0:
                questions.append(text_content)
            else:
                answers.append(text_content)

        return questions,answers
    
    # get the beatifulSoup of this website
    r = requests.get(conversation_website)
    soup = BeautifulSoup(r.content, 'html.parser')

    # the divs of those conversation all have id
    # first question and answer are with id 0 and 1 respectively. The second Q&A have 2 and 3 and so on.
    ids = getAllIdsOfAHtml(soup)

    if (len(ids)%2!=0):  # cause Q&A appear as pairs, its len must be even number
        print(conversation_website + "has odd Q&A which is inconvenient to divide the conversation into Q and A")
        return None

    # extract all questions and answers
    questions,answers = getAllQA(soup, ids)
    # print(questions)
    # print(answers)

    # assemble a json string of the extracted conversation
    conversation_num = int(len(ids)/2)
    conversation_dict = {'url':conversation_website.split('/')[-1], 'num':conversation_num, 'q':questions , 'a':answers}
    # conversation_jsonStr = json.dumps(conversation_dict)

    return conversation_dict

# the pages of catalogue to webscrape 
start_pages = 1100
total_pages = 1206

catalog_link_prefix = "https://sharegpt.com/explore/new?page="
conversation_page_link_prefix = "https://sharegpt.com/"

saving_dir = "./conversation_jsons"

# configure of chrome driver and selemium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service = s,options=chrome_options)
driver.maximize_window()

time_st = time.time()

# sometimes the conversation will occur more than one time
conversation_set = set() # check if there is duplicate conversation

# iterate each page of the sharegpt
for i in range(start_pages,total_pages):

    # count the times of waiting the website refresh its list of conversations
    wait_count = 0

    # the list of jsons in the current page (its len at most 50)
    json_list = []
    
    # If we wait too long, we need to reaccess this webpage
    while len(json_list) ==0:
        wait_count = 0
        # use chrome driver to access sharegpt (a dynamic website)
        driver.get(catalog_link_prefix + str(i))
        
        while len(json_list) ==0 and wait_count<6:
            time.sleep(10) # wait this dynamic website load everything
            print(catalog_link_prefix + str(i))

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Getting the title tag
            divs = soup.find_all('div', class_='grid gap-2 flex-1')

            # Iterate each div to get each conversation
            for div in divs:
                conversation_link = div.find('a').get('href')
                print(conversation_link)
                if conversation_link in conversation_set:
                    # print("This conversation has been found")
                    continue
                
                # access the link of the conversation and extract a json dictionary
                conversation_dict = extractConversationFrom(conversation_page_link_prefix + conversation_link)
                
                if conversation_dict != None:
                    json_list.append(conversation_dict)
                    conversation_set.add(conversation_link)

            # Because the website will stay the same before it return our page query. (almost in 10s)
            if len(json_list) == 0:
                print("The page have not been refreshed... Wait another 10s")

            wait_count += 1
    
        
    # write the json list file so that we can save the conversation in the current page
    file_name = "page_" + str(i)
    file_path = os.path.join(saving_dir, file_name)
    with open(file_path, 'w') as jsonlist_file:
        json.dump(json_list, jsonlist_file)
    
    # Output time cost and current epoch
    cur_time = time.time()
    print("Finish page %d and current total cost time: %5f" % (i, cur_time - time_st))

