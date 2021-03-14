from facebook_scraper import get_posts
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import json

page_name = 'columbiaconfessionz'

posts = []

output_data = []

analyzer = SentimentIntensityAnalyzer()

for i, post in enumerate(get_posts(page_name, pages=10)):
    if post['text'] is not None:
        vs = analyzer.polarity_scores(post['text'])
        post['time'] = post['time'].strftime('%m/%d/%Y')

        post['sentiment'] = vs['compound']

        post_num = post['text'].split(' ')[0].replace('.', '')

        post["confession_num"] = post_num

        #x = mycol.insert_one(post)

        output_data.append(post)

print(output_data)
