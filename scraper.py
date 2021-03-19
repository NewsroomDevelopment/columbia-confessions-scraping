from facebook_scraper import get_posts
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import json
from facebook_scraper import get_posts
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from pprint import pprint
import os

# Load environment variables
load_dotenv(find_dotenv())

# Connect to MongoDB
MDB_USERNAME = os.getenv('MDB_USERNAME')
MDB_PASSWORD = os.getenv('MDB_PASSWORD')
MDB_URI = f'mongodb+srv://{MDB_USERNAME}:{MDB_PASSWORD}@confessions.scrus.mongodb.net/confessions?retryWrites=true&w=majority'
client = MongoClient(MDB_URI)

mydb = client["confessions_database"]
mycol = mydb["confessions"]

page_name = 'columbiaconfessionz'

posts = []

output_data = []

analyzer = SentimentIntensityAnalyzer()

for i, post in enumerate(get_posts(page_name, pages=3)):
    #print('hi')
    if post['text'] is not None:
        
        
        time = post['time'].strftime('%m/%d/%Y')
        post_id = post["post_id"]
        post_url = post["post_url"]
        
        #find first confession_num
        first_conf_num = ''
        found_num = False
        k = 0
        while not found_num:
            if post['text'][k].isdigit():
                first_conf_num = first_conf_num + post['text'][k]
                if not post['text'][k+1].isdigit():
                    found_num = True
            k+=1
                
        
        
        confession_num = int(first_conf_num)
        
        #finds index of next post num and appends to list
        list_of_idx = []
        next_post = True
        confession_nums = []
        
        next_num = confession_num
        while next_post:
            x = post['text'].find(str(next_num))
            if x != -1:
                list_of_idx.append(x)
                confession_nums.append(next_num)
            else:
                list_of_idx.append(-1)
                next_post = False
            next_num = next_num+1
        #print(post['text'])
        #print(confession_nums)
        #print(list_of_idx)
            
        
        posts_in_post = []
        for idx in range(0,len(list_of_idx)):
            if list_of_idx[idx] != -1:
                posts_in_post.append(post['text'][list_of_idx[idx]:list_of_idx[idx+1]])
        #print(posts_in_post)    
                              
        for j in range(len(posts_in_post)):                     
            vs = analyzer.polarity_scores(posts_in_post[j])
            post_data = {
                'text': posts_in_post[j],
                'sentiment': vs['compound'],
                'likes': post['likes'],
                'comments': post['comments'],
                'shares': post['shares'],
                'time': time,
                'post_url': post_url,
                'confession_num': confession_nums[j]
            }

            if post_id:  
                post_data["_id"] = post_id + chr(j+65)
            else:
                post_data["_id"] = post_url[(post_url.find("id=") + 3) : post_url.find("&id=")] + chr(j+65)
        
            output_data.append(post_data)
    #print('---------------------')

print(len(output_data))

test_output_data = output_data[0:2]
for post_data in output_data:
    myquery = {"id_": post_data["_id"]}
    result = list(mycol.find(myquery))
    print("result " + result)
    print("len: " + len(result))
    #

    if (len(result) == 0):
        mycol.insert_one(post_data)
        print("not found, inserted")
    else:
        updated_info = {"$set": {'likes': post_data['likes'], 
                                 'comments': post_data['comments'], 
                                 'shares': post_data['shares']}}
        mycol.update_one(myquery, updated_info)
        print("updated")