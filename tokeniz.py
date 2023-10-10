import pandas as pd
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import numpy as np
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
import re


df = pd.read_csv('IMDB dataset.csv')


df['review'] = df.review.apply(lambda x: re.sub(r'@[^ ]*',r'',x))


def preprocess(text):
    t = text.lower()
    # t = re.sub('_',r'',t)
    # t = re.sub('\d+',r'',t)
    t = re.sub(r'@[^ ]*',r'',t)
    t = re.sub(r'\W+',r' ',t)
    t = re.sub(r'(https|quot|http)', '', t)
    t = re.sub(r'\b(?!(?:ai)\b)\w{3}\b','', t)
    t = re.sub(r'http?://\S+|www\.\S+','',t)
    stopwords_list = stopwords.words('english')
    txt = ' '.join([word for word in t.split() if word not in stopwords_list])
    return txt

lemmatizer = WordNetLemmatizer()



df['prepro'] = [' '.join([lemmatizer.lemmatize(preprocess(email))])
                 .strip() for email in df['review']]


texts = df.prepro.values
labels = df.sentiment.values


from keras.preprocessing.text import Tokenizer

tokenizer = Tokenizer()
tokenizer.fit_on_texts(texts)