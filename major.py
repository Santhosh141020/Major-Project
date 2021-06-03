import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from skimage.io import imread,imshow,imshow_collection
import re
import contractions
import nltk
from nltk.tokenize.toktok import ToktokTokenizer
nltk.download('stopwords')
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#defined to get urls of indicated product

#to get reviews
def get_reviews(dic,new):
  dic=get_urls(name)
  review_link=[]
  reviews=[]
  url=dic[new][0]

  page1=requests.get(url)
  soup=BeautifulSoup(page1.content,"html.parser")
  
  for r in soup.findAll("div",attrs={"class":"t-ZTKy"}):
    reviews.append(r.get_text())
  return reviews

def get_urls(name):
  links=[]
  products=[]
  img_links=[]
  dic={}

  try :
    name=name.replace(' ','%20')
  except:
    pass

  url='https://www.flipkart.com/search?q='+name+'&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off'
  print(url)

  page=requests.get(url)
  soup=BeautifulSoup(page.content,"html.parser")

  if soup.findAll("a",attrs={"class":"_1fQZEK"}) != []:
    for link in soup.findAll("a",attrs={"class":"_1fQZEK"}):
      n_link=link.get('href')
      links.append(n_link)
    for link in soup.findAll("img",attrs={"class":"_396cs4 _3exPp9"}):
      n_link=link.get('src')
      img_links.append(n_link)
    for product in soup.findAll("div",attrs={"class":"_4rR01T"}):
      products.append(product.get_text())

  elif soup.findAll("a",attrs={"class":"s1Q9rs"}) != [] :
    for link in soup.findAll("a",attrs={"class":"s1Q9rs"}):
      n_link=link.get('href')
      links.append(n_link)
      products.append(link.get_text())
    for link in soup.findAll("img",attrs={"class":"_396cs4 _3exPp9"}):
      n_link=link.get('src')
      img_links.append(n_link)

  else :
    for link in soup.findAll("a",attrs={"class":"IRpwTa"}):
      n_link=link.get('href')
      links.append(n_link)
    for link in soup.findAll("img",attrs={"class":"_2r_T1I"}):
      n_link=link.get('src')
      img_links.append(n_link)
    for product in soup.findAll("div",attrs={"class":"_2WkVRV"}):
      products.append(product.get_text())

  for i in range(len(links)):
    links[i]="https://www.flipkart.com"+links[i]
    if img_links[i]=='':
      img_links[i]='http://fremontgurdwara.org/wp-content/uploads/2020/06/no-image-icon-2.png'
    dic[products[i]]=[links[i],img_links[i]]
    
  return dic


# Remove HTML Tag
def html_tag(text):
  Soup = BeautifulSoup(text,"html.parser")
  new_text = Soup.get_text()
  return new_text

html_tag('<html><h2> some important info </h2></html>')

# Expand Contractions
def con(text):
  expand= contractions.fix(text)
  return expand

con("I don't like you" ) 

#Remove Special Characters
def remove_sp(text):
  pattern = r'[^A-Za-z0-9\s]'
  text = re.sub(pattern,'',text)
  return text

def remove_stopwords(text):

  #creating a stopword list 
  stopword_list = nltk.corpus.stopwords.words('english')
  stopword_list.remove('no')
  stopword_list.remove('not')
  stopword_list.append('read')
  
  len(stopword_list)

  #removing the stop words
  tokenizer = ToktokTokenizer()
  tokens = tokenizer.tokenize(text)
  tokens = [token.strip() for token in tokens]
  filtered_tokens = [token for token in tokens if token not in stopword_list]
  filtered_text = ' '.join(filtered_tokens)
  return filtered_text


import streamlit as st
st.title('Sentimental Analysis On Flipkart Products')
#taking first input
name=st.text_input('Enter The Product Name To Be Analysed','Type Here')
if st.button('confirm') or name != '':
  dic=get_urls(name)
  for str in dic.keys():
    st.write(str)

  #taking second input  
  new=st.text_input('Copy the perfect name of the product of your interest from the above list')
  if st.button('Yes my interest is true') or new !='':
    reviews=get_reviews(dic,new)
    for i in range(len(reviews)):
      reviews[i]= reviews[i].lower()
      reviews[i]= html_tag(reviews[i])
      reviews[i]= con(reviews[i])
      reviews[i]= remove_sp(reviews[i])
      reviews[i]= remove_stopwords(reviews[i])
    #done preprocessing
    Analyze = SentimentIntensityAnalyzer()
    compound1=[]
    emoji=[]
    for x in range(len(reviews)):
      compound1.append(Analyze.polarity_scores(reviews[x])['compound'])
    for x in range(len(reviews)):
      if compound1[x]>=0.8:
        emoji.append('\U0001F600\U0001F600\U0001F600')
      elif compound1[x]<0.8 and compound1[x]>0.1:
        emoji.append('\U0001F642\U0001F642')
      elif compound1[x]<=0.1:
        emoji.append('\U0001F611')

    #dic=get_urls(name)
    pic = imread(dic[new][1])
    col1, col2, col3 = st.beta_columns([1,1,1])
    col2.image(pic, use_column_width=True, caption=new)

    
    df1 = pd.DataFrame({'Reviews':reviews,
                    'Compound Score': compound1,'Emojis':emoji})
    
    col1, col2, col3 = st.beta_columns([0.01,1,0.1])
    if df1.empty :
      col2.write('Reviews Not Available')
    else : 
      
      col2.dataframe(df1.style.set_properties(**{'background-color': 'grey', 'text-align': 'center', 'color':'black', 'border-color':'green', 'border-width':20}))

# Done Sentimental Analysis'''