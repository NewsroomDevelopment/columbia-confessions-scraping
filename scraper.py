from facebook_scraper import get_posts
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import json
from facebook_scraper import get_posts
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from pprint import pprint
from datetime import datetime
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

# start_date = datetime(2021, 1, 18)
for i, post in enumerate(get_posts(page_name, pages=10, options={"comments": True, "reactors": True}, cookies="cookies.json", extra_info=True)):
    
    # if post['time'] > start_date:
    #     print('date is ' + post['time'].strftime('%m/%d/%Y'))
    #     print('skipping...')
    #     continue
    try:
        if post['text'] is not None:

            time = post['time'].strftime('%m/%d/%Y')
            post_id = post["post_id"]
            post_url = post["post_url"]

            # find first confession_num
            first_conf_num = ''
            found_num = False
            k = 0
            while not found_num and k < len(post['text']) - 1:
                if post['text'][k].isdigit():
                    first_conf_num = first_conf_num + post['text'][k]
                    if not post['text'][k+1].isdigit():
                        found_num = True
                k += 1

            confession_num = int(first_conf_num)

            # finds index of next post num and appends to list
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
            # print(post['text'])
            # print(confession_nums)
            # print(list_of_idx)

            posts_in_post = []
            for idx in range(0, len(list_of_idx)):
                if list_of_idx[idx] != -1:
                    posts_in_post.append(
                        post['text'][list_of_idx[idx]:list_of_idx[idx+1]])
            # print(posts_in_post)
            comments_full = [{
                'commenter_name': comment['commenter_name'],
                'comment_text': comment['comment_text'],
                'comment_time': comment['comment_time'],
                'comment_reactions': comment['comment_reactions']
            } for comment in post['comments_full']]

            for j in range(len(posts_in_post)):
                vs = analyzer.polarity_scores(posts_in_post[j])
                post_data = {
                    'text': posts_in_post[j],
                    'sentiment': vs['compound'],
                    'likes': post['likes'],
                    'comments': post['comments'],
                    'comments_full': comments_full,
                    'reactions': post['reactions'],
                    'shares': post['shares'],
                    'time': time,
                    'post_url': post_url,
                    'confession_num': confession_nums[j]
                }

                if post_id:
                    post_data["_id"] = post_id + chr(j+65)
                else:
                    post_data["_id"] = post_url[(post_url.find(
                        "id=") + 3): post_url.find("&id=")] + chr(j+65)

                myquery = {"_id": post_data["_id"]}
                result = mycol.count_documents(myquery)
                print(time)
                if (result == 0):
                    mycol.insert_one(post_data)
                    print("not found, inserted")
                else:
                    updated_info = {"$set": {'likes': post_data['likes'],
                                            'comments': post_data['comments'],
                                            'shares': post_data['shares'],
                                            'comments_full': post_data['comments_full'],
                                            'reactions': post_data['reactions']
                                            }
                                    }
                    mycol.update_one(myquery, updated_info)
                    print("updated")    # print('---------------------')
    except Exception as e:
        continue

