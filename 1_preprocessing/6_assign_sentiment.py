import pandas as pd
import re
import unicodedata
import nltk
from nltk.corpus import stopwords
from textblob_de import TextBlobDE as TextBlob #2

from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from langdetect import detect
import torch
from transformers import pipeline, set_seed

df = pd.read_csv("converted/dataset_complete.csv", encoding="utf-8")

def basicpreprocess(text):
  text = unicodedata.normalize('NFKD', text)
  text = ''.join(c for c in text if (unicodedata.category(c) in ['Ll', 'Lm', 'Lu', 'Mn']) or c in [' ', '-'])
  if len(text) > 1000:
    print(text)
  return text

stop_words = set(stopwords.words("german"))

def advancedpreprocess(text):
  text = text.lower()
  tokens = word_tokenize(text)
  tokens = [token for token in tokens if token not in stop_words]
  stemmer = SnowballStemmer("german")
  stemmed_tokens = [stemmer.stem(token) for token in tokens]
  stemmed_text = " ".join(stemmed_tokens)
  return stemmed_text

df['title_subtitle'] = (df['title'].fillna('') + ' ' + df['subtitle'].fillna('')).str.strip().str.replace(r'\s+', ' ')

df['titlesubtitle_prepr'] = df['title_subtitle'].apply(basicpreprocess)
df['titlesubtitle_prepr_adv'] = df['titlesubtitle_prepr'].apply(advancedpreprocess)

print(df['titlesubtitle_prepr'])
print(df['titlesubtitle_prepr_adv'])

df['keywords_cleaned'] = df['keywords'].str.replace('|', ' ')
df['keywords_cleaned'].fillna('', inplace=True)
print(df['keywords_cleaned'])

df['keywords2_cleaned'] = df['keywords2'].astype(str).apply(lambda x: [kw for kw in x.split('|') if not kw.startswith('(')])
df['keywords2_cleaned'] = df['keywords2_cleaned'].apply(lambda x: ' '.join(x))
df['keywords2_cleaned'].fillna('', inplace=True)
print(df['keywords2_cleaned'])

df['alltext'] = (df['title_subtitle'].fillna('') + ' ' + df['keywords_cleaned'].fillna('') +  ' ' + df['keywords2_cleaned'].fillna('')).str.strip().str.replace(r'\s+', ' ')

df['alltext_prepr'] = df['alltext'].apply(basicpreprocess)
df['alltext_prepr_adv'] = df['alltext_prepr'].apply(advancedpreprocess)



# Sentiment Analysis
def sentiment_analysis_lexi(text):
    blob = TextBlob(text) 
    sentiment = blob.sentiment.polarity
    return sentiment

df["title_sentiment"] = df["titlesubtitle_prepr"].apply(sentiment_analysis_lexi)

df["alltext_sentiment"] = df["alltext_prepr"].apply(sentiment_analysis_lexi)


# Sentiment Analysis AI
set_seed(42)
model = pipeline("sentiment-analysis", model="distilbert-base-german-cased", truncation=True, max_length=512)

def sentiment_analysis_AI(text):
    result = model(text)[0]
    return result["score"]

df["title_sentiment_AI"] = df["titlesubtitle_prepr"].apply(sentiment_analysis_AI)

df["alltext_sentiment_AI"] = df["alltext_prepr"].apply(sentiment_analysis_AI)

df.to_csv("converted/dataset_complete_sentiment2.csv", index=False)
