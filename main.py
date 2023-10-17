import json
import time
import subprocess
from datetime import datetime
import pandas as pd
from fastapi import FastAPI
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
from tokenization import tokenizer
import requests


# fastAPI

app = FastAPI()

@app.get("/")
def read_root():
   return {"Welcome to": "Good News",
           "To generate token visit":"/gen_token",
           "To view articles visit":"/good_news"}

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

    # lists for df
    title = []
    date = []
    url = []
    prediction = []
    holc_prediction = []

    api = 'b456a0b678604587bd37dfe28a0bf520'

    base_url = 'https://newsapi.org/v2/everything'

    params = {
        'source': 'bbc-news',
        'q': '+good',
        'language': 'en',
        'sortBy': 'publishedAt',
        'apiKey': api
    }

    gathered_articles = requests.get(base_url, params=params)

    data = gathered_articles.json()

    articles = data['articles']

    #IAM
    generatedTokens = pd.read_csv("generatedTokens.csv")
    ca_accessToken = generatedTokens["access_token"].iloc[-1]
    
    # fetch sentiment analysis results
    model = tf.keras.models.load_model('new.h5')

    for article in articles[:5]:
        og_date = pd.to_datetime(article['publishedAt'])
        formatted_date = og_date.strftime("%A %dth of %B at %H:%M:%S")
        txt_seq = tokenizer.texts_to_sequences([article['content']])
        pad_seq = pad_sequences(txt_seq, maxlen=100, padding='post')
        pred = model.predict(pad_seq)
        if np.argmax(pred) == 0:
            if article['title'] != '[Removed]':
                title.append(article['title'])
                date.append(formatted_date)
                url.append(article['url'])
                prediction.append(pred[np.argmax(pred)][0])
        #holc prediction
        holc_data = {'text': article['content'],'accessToken': ca_accessToken}
        holc_response = requests.post("https://csat.alamedaproject.eu/classes", json=holc_data)
        holc_response_json = holc_response.json()
        # if holc_response_json['sentiment_classes'][0]['sentiment_score'] > 0:
        holc_prediction.append(holc_response_json['sentiment_classes'][0]['sentiment_score'] * 0.01)
        holc_response.close()

    df = pd.DataFrame([title,date,url,prediction,holc_prediction]).T
    df.columns = ['title','date','url','prediction','holc_prediction']
    df = df.sort_values(by='prediction', ascending=False)
    # try:
    #     with pd.ExcelWriter('articles.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
    #         df.to_excel(writer, index=True, header=True, sheet_name='Sheet1')
    # except FileNotFoundError:
    df.to_excel('articles.xlsx')

    df_json = json.loads(df.iloc[:10].to_json(orient='records'))
    return df_json
    


# server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)