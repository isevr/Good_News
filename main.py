import requests
import pandas as pd
import subprocess
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

# fastAPI

app = FastAPI()

@app.get("/")
def read_root():
   return {"Welcome to": "Some Good News"}

# generate token for iam
@app.get("/gen_token")
def generate_token():
    process = subprocess.Popen(["python", "refresh_generated_token.py"])
    tokens = pd.read_csv('generatedTokens.csv')
    time.sleep(10)
    process.terminate()
    process.wait()
    return {"Token":tokens.iloc[-1]}


# fetch articles
@app.get("/good_news/")
def all_articles():
    api = 'b456a0b678604587bd37dfe28a0bf520'

    base_url = 'https://newsapi.org/v2/everything'

    params = {
        'source': 'bbc-news',
        'q': 'world',
        'sortBy': 'publishedAt',
        'apiKey': api
    }

    gathered_articles = requests.get(base_url, params=params)

    data = gathered_articles.json()

    articles = data['articles']


# token access to CSAT

    generatedTokens = pd.read_csv("generatedTokens.csv")
    ca_accessToken = generatedTokens["access_token"].iloc[-1]

    # fetch sentiment analysis results
    responses = []

    for article in articles[:5]:
        article_response = {}
        data = {'text': article['description'],'accessToken': ca_accessToken}
        response = requests.post("https://csat.alamedaproject.eu/classes", json=data)
        article_response['title'] = article['title']
        article_response['content'] = article['content']
        article_response['date'] = article['publishedAt']
        article_response['url'] = article['url']
        article_response['response'] = response.json()
        responses.append(article_response)
        response.close()
        
    # dataframe creation
    title = []
    date = []
    url = []

    for response in responses:
        # can adjust confidence level
        if response['response']['sentiment_classes'][0]['sentiment_score'] > 0:   # positive: 0, neutral: 1, negative: 2
            title.append(response['title'])
            date.append(response['date'])
            url.append(response['url'])


    df = pd.DataFrame([title,date,url]).T
    df.columns = ['title','date','url']

    df_json = json.loads(df.to_json(orient='records'))
    return df_json
    


# server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)