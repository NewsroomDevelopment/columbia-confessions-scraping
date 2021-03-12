from facebook_scraper import get_posts
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

page_name = 'columbiaconfessionz'

posts = []
for post in get_posts(page_name, pages=10):
  posts.append(post['text'])
print(len(posts))

compoundScores = []
analyzer = SentimentIntensityAnalyzer()
for post in posts:
    vs = analyzer.polarity_scores(post)
    compoundScores.append(vs['compound'])
    print("{:-<65} {}".format(post, str(vs['compound'])))
