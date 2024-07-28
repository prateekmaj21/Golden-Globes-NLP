import warnings
warnings.filterwarnings('ignore')

#importing libraries
import pandas as pd
import numpy as np
import re
from collections import defaultdict

#importing spacy libraries
import spacy
nlp = spacy.load("en_core_web_sm")

import nltk
nltk.download
nltk.download("stopwords")
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

from nltk import word_tokenize, pos_tag, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer

df = pd.read_json("gg2013.json")

#finds all hashtags and add to hashtag column
df["hashtag"] = df["text"].apply(lambda x: re.findall(r"#(\w+)",x))

#finds all mentions and add to mention column
df["mention"] = df["text"].apply(lambda x: re.findall(r"@(\w+)",x))

#Drop duplicate columns
df.drop_duplicates(subset="text",inplace=True)

#remove un clean text
df['text'] = df['text'].str.replace('https?://\S+|www\.\S+|ftp://\S+', '')
df['text'] = df['text'].str.replace('GoldenGlobes', '')
df['text'] = df['text'].str.replace('goldenglobes', '')
df['text'] = df['text'].str.replace('[G|g]olden\s?[G|g]lobes*', '')

#remove numbers
df['text'] = df['text'].astype(str).str.replace('\d+', '')

#remove punctuation
df['text'] = df['text'].str.replace('[^\w\s]','')

#remove other characters
df['text'] = df['text'].str.replace('#|@|RT', '')

#lemmatize text
lemmatizer = nltk.stem.WordNetLemmatizer()
w_tokenizer =  TweetTokenizer()

def lemmatize_text(text):
  return [(lemmatizer.lemmatize(w)) for w in w_tokenizer.tokenize((text))]

#remove any punctuations
def remove_punctuation(words):
  new_words = []
  for word in words:
    new_word = re.sub(r'[^\w\s]','', (word))
    if new_word != '':
        new_words.append(new_word)
  return new_words

words = df['text'].apply(lemmatize_text)
df["bagOfWords"] = words.apply(remove_punctuation)

df_awards = pd.DataFrame()
df_awards['newText'] = df["bagOfWords"].apply(lambda x:' '.join(x))


newDF = pd.DataFrame()
newDF['text'] = df['text'].str.lower()

def extract_award_name(text):
    pattern = re.compile(r'best (?:actress|actor|screenplay|motion picture|director|screenplay|original score|original song|animated feature film)(?: (?:in a )?(?:motion picture|mini-series|tv|movie|film|drama|comedy or musical))?', re.IGNORECASE)
    matches = pattern.findall(text)
    return ', '.join(set(matches)) if matches else None

df = pd.DataFrame(newDF['text'])
# Apply function to DataFrame
df['award_names'] = newDF['text'].apply(extract_award_name)

# Filter rows
df_with_awards = df[df['award_names'].notna()]


top15awards = df_with_awards['award_names'].value_counts()[:15].index.tolist()

def returnWordCnts(findStr,df_awards):
  df_awards = df_awards[df_awards['newText'].str.contains(findStr)].reset_index(drop=True)
  df_awards['nouns'] = df_awards['newText'].apply(lambda x: [*nlp(x).ents])

  #removing rows with empty list of nouns
  df_awards = df_awards[df_awards['nouns'].apply(lambda x: len(x)>1)]

  #Creating New dataframe to store all nouns as separate to get count
  NewList =[str(j) for i in df_awards['nouns'] for j in i]
  dfBestActreesNewDf = pd.DataFrame(NewList,columns=['values'])

  return dfBestActreesNewDf.value_counts()

#Getting Host Names
def getHosts():
  hosts = returnWordCnts("host|Host",df_awards)
  hostsL = hosts[:2].index.tolist()
  hostsL = [i[0] for i in hostsL]
  hostss = ' and '.join(hostsL)
  return hostss

Hosts = getHosts()

#Getting at most 5 nominees for each 15 awards
def getAwardNominees(top15):
  newAwardL = []
  for eachAward in top15:
    awrd = returnWordCnts(eachAward,df_awards)
    awrdL = awrd[:5].index.tolist()
    awrdsL = [i[0] for i in awrdL]
    awrdss = ' , '.join(awrdsL)
    newAwardL.append(awrdsL)
  return newAwardL
  print("Nominees of the award",eachAward ," are :", awrdss)


listOfNominees = getAwardNominees(top15awards)

def getAwardandWinners(top15):
    newAwardL = []
    for eachAward in top15:
        awrd = returnWordCnts(eachAward, df_awards)
        awrdL = awrd[:2].index.tolist()
        if len(awrdL) > 0 and len(awrdL[0]) > 0:  # Ensure awrdL and awrdL[0] have elements
            newAwardL.append(awrdL[0][0])
        else:
            newAwardL.append('NA')  # or handle this case as needed
    return newAwardL

awardWinnerList = getAwardandWinners(top15awards)

#Getting List of Award Presenters
def getAwardPresenter():
  hosts = returnWordCnts("award presenters|Award presenters|award presenter|Award presenter|award Presenter",df_awards)
  hostsL = hosts[2:].index.tolist()
  hostsL = [i[0] for i in hostsL]
  hostss = ' and '.join(hostsL)
  return hostss

#Getting Host Names
def getBestDressed():
  hosts = returnWordCnts("best dressed tonight|Best Dressed Tonight|Best dressed tonight",df_awards)
  hostsL = hosts[:10].index.tolist()
  hostsL = [i[0] for i in hostsL]
  return hostsL[1]

def getWorstDressed():
  hosts = returnWordCnts("worst dressed|Worst Dressed|Worst dressed",df_awards)
  hostsL = hosts[:10].index.tolist()
  hostsL = [i[0] for i in hostsL]
  return hostsL[3]

def mostControversial():
  hosts = returnWordCnts("Controversial|controversial",df_awards)
  hostsL = hosts[:10].index.tolist()
  hostsL = [i[0] for i in hostsL]
  return hostsL[2]

print("Hosts of this event are :",Hosts,'\n')
print("Presenters of the awards are ",getAwardPresenter(),'\n')
for i,j in enumerate(top15awards):
  print("Nominees of the award",j ," are :", ' '.join(listOfNominees[i]))
  print("Winner of the award",j ," is :", awardWinnerList[i],"\n")

print("Best dressed :",getBestDressed(),'\n')
print("Worst dressed :",getWorstDressed(),'\n')
print("Most controversial :",mostControversial(),'\n')







