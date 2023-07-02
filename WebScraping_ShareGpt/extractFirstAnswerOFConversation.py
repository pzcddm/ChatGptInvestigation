'''
This python script is to extract the content of those jsonList stored in directory "conversation_jsons"
The format of those jsonLists have been discribed in webScraping.py
One jsonList corresponds to a page in the catalogue of sharegpt

After preprossesing, the tokenized conversation will be stored in directory "tokenized_answers"
This script has two main features:
    1. identify those English Answers
    2. onlu extract the first answer of conversations
    3. filter those too short answer

'''
import json
import os
import numpy as np
from transformers import GPT2TokenizerFast
import nltk
from nltk.corpus import words
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
nltk.download('words')
nltk.download('punkt')

def is_english_sentence(text):
    """
    Check if a given string is an English sentence.

    Parameters:
    text (str): The string to check.

    Returns:
    bool: True if the string is likely to be an English sentence, False otherwise.
    """
    
    # tokenizing the sentence into words
    word_list = nltk.word_tokenize(text)

    # converting all words to lower case
    word_list = [word.lower() for word in word_list]

    # using set to remove duplicate words
    word_set = set(word_list)

    # check if each word in the sentence is in the English corpus
    english_words = set(words.words())
    common_elements = word_set.intersection(english_words)

    # if more than 50% of unique words are in the English corpus, we assume it's an English sentence
    return len(common_elements) / len(word_set) > 0.5

# settings of directory
jlists_file_dir = "./conversation_jsons"
jlists_filename_prefix = "page_"
saving_file_path = "./tokenized_answers/1st_english_answers.bin"
max_page_no = 1205
conversation_set = set()
answer_len_filter = 50

### Tokenize each answer
tokenized_answers = []
# iterate each json list and extract its answers
for i in range(1, max_page_no):
    jlist_file_path = os.path.join(jlists_file_dir,jlists_filename_prefix + str(i))
    jsonlist = []
    with open(jlist_file_path, 'r') as f:
        jsonlist = json.load(f)
    
    for conversation_js in jsonlist:
        # there is a duplicate conversation, skip it
        if conversation_js['url'] in conversation_set:
            # print("there is duplicate url, skip it")
            continue

        answers = conversation_js['a']

        if len(answers) == 0:
            continue
        # if the answer is too short
        if len(answers[0]) <= answer_len_filter:
            continue

        # if it is not a English answer then skip it
        if is_english_sentence(answers[0]) == False:
            continue

        conversation_set.add(conversation_js['url'])
        for a in answers:
            tokenized_answers.append(tokenizer(a)['input_ids'])

print("Tokenization Complete the amount of total answers: " + str(len(conversation_set)))

short_answers_amount = 0
zero_answers_amount = 0
for tokens in tokenized_answers:
    # remove all the blank
    tokens = [i for i in tokens if i != 220]
    if len(tokens)<64:
        short_answers_amount += 1
    if len(tokens) == 0: 
        zero_answers_amount += 1

print("zero_answers_amount" + str(zero_answers_amount))
print("short_answers_amount" + str(short_answers_amount))
print("total answers amount" + str(len(tokenized_answers)))

### Write tokenized Dataset to the binary file
saving_file = open(saving_file_path,'wb')
for tokens in tokenized_answers:
    tokens_len =int(len(tokens))
    # write its length
    saving_file.write(tokens_len.to_bytes(4,byteorder='little',signed=True))
    # write the list of tokens
    saving_file.write(np.array(tokens,dtype=np.uint32).tobytes())

# close the file writing stream
saving_file.close()
print(saving_file_path + "written")