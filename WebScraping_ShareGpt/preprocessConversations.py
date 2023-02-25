'''
This python script is to extract the content of those jsonList stored in directory "conversation_jsons"
The format of those jsonLists have been discribed in webScraping.py
One jsonList corresponds to a page in the catalogue of sharegpt

After preprossesing, the tokenized conversation will be stored in directory "tokenized_answers"
(Currently, we only want to get the content of tokenized answers)

'''
import json
import os
import numpy as np
from transformers import GPT2TokenizerFast
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

# the range of pages we want to tokenize
start_pages = 1
end_pages = 200

# settings of directory
jlists_file_dir = "./conversation_jsons"
jlists_filename_prefix = "page_"
saving_file_path = "./tokenized_answers/answers_%d_%d"%(start_pages, end_pages)

conversation_set = set()

### Tokenize each answer
tokenized_answers = []
# iterate each json list and extract its answers
for i in range(start_pages, end_pages+1):
    jlist_file_path = os.path.join(jlists_file_dir,jlists_filename_prefix + str(i))
    jsonlist = []
    with open(jlist_file_path, 'r') as f:
        jsonlist = json.load(f)
    
    for conversation_js in jsonlist:
        # there is a duplicate conversation, skip it
        if conversation_js['url'] in conversation_set:
            continue
        
        conversation_set.add(conversation_js['url'])
        answers = conversation_js['a']
        for a in answers:
            tokenized_answers.append(tokenizer(a)['input_ids'])
print("Tokenization Complete the amount of total answers: " + str(len(conversation_set)))

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