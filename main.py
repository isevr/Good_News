import json
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
   return {"Welcome to": "Some Good News"}


# fetch articles
@app.get("/good_news/")
def all_articles():

    # lists for df
    title = []
    date = []
    url = []
    prediction = []

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


    # fetch sentiment analysis results
    model = tf.keras.models.load_model('new.h5')

    for article in articles[:100]:
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

            # responses.append(article)
        


    # for response in responses:
    #     if response['title'] != '[Removed]':
    #         title.append(response['title'])
    #         date.append(response['publishedAt'])
    #         url.append(response['url'])


    df = pd.DataFrame([title,date,url,prediction]).T
    df.columns = ['title','date','url','prediction']
    df = df.sort_values(by='prediction', ascending=False)
    df.to_excel('articles.xlsx')

    df_json = json.loads(df.iloc[:10].to_json(orient='records'))
    return df_json
    


# server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)