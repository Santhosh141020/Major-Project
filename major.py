import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from emot.emo_unicode import UNICODE_EMO
import contractions
import nltk
from nltk.tokenize.toktok import ToktokTokenizer
nltk.download('stopwords')
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import streamlit as st


def get_urls(name):
    links = []
    products = []
    img_links = []
    dic = {}

    if name == '':
        return(dic)

    try:
        name = name.replace(' ', '%20')
    except:
        pass

    url = 'https://www.flipkart.com/search?q=' + name + '&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off'
    # print(url)

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    if soup.findAll("a", attrs={"class": "_1fQZEK"}) != []:
        for link in soup.findAll("a", attrs={"class": "_1fQZEK"}):
            n_link = link.get('href')
            links.append(n_link)
        for link in soup.findAll("img", attrs={"class": "_396cs4 _3exPp9"}):
            n_link = link.get('src')
            img_links.append(n_link)
        for product in soup.findAll("div", attrs={"class": "_4rR01T"}):
            products.append(product.get_text())

    elif soup.findAll("a", attrs={"class": "s1Q9rs"}) != []:
        for link in soup.findAll("a", attrs={"class": "s1Q9rs"}):
            n_link = link.get('href')
            links.append(n_link)
            products.append(link.get_text())
        for link in soup.findAll("img", attrs={"class": "_396cs4 _3exPp9"}):
            n_link = link.get('src')
            img_links.append(n_link)

    else:
        brand = []
        model=[]
        for link in soup.findAll("a", attrs={"class": "IRpwTa"}):
            n_link = link.get('href')
            model.append(link.get_text())
            links.append(n_link)
        for link in soup.findAll("img", attrs={"class": "_2r_T1I"}):
            n_link = link.get('src')
            img_links.append(n_link)
        for product in soup.findAll("div", attrs={"class": "_2WkVRV"}):
            brand.append(product.get_text())
        for i in range(len(brand)):
          products.append(brand[i]+ ' '+model[i])
          

    for i in range(len(links)):
        links[i] = "https://www.flipkart.com" + links[i]
        if img_links[i] == '':
            img_links[i] = 'image.png'
        dic[products[i]] = [links[i], img_links[i]]

    return dic

def get_reviews( dic, new):
    reviews = []
    url = dic[new][0]

    page1 = requests.get(url)
    soup = BeautifulSoup(page1.content, "html.parser")

    for r in soup.findAll("div", attrs={"class": "t-ZTKy"}):
        reviews.append(r.get_text())
    return reviews

# Remove HTML Tag
def html_tag(text):
    Soup = BeautifulSoup(text,"html.parser")
    new_text = Soup.get_text()
    return new_text

# Expand Contractions
def con(text):
  expand= contractions.fix(text)
  return expand

#Remove Special Characters
def remove_sp(text):
  pattern = r'[^A-Za-z0-9\s]'
  text = re.sub(pattern,'',text)
  return text

#Remove stopwords
def remove_stopwords(text):
    # creating a stopword list
    stopword_list = nltk.corpus.stopwords.words('english')
    stopword_list.remove('no')
    stopword_list.remove('not')
    stopword_list.append('read')

    len(stopword_list)

    # removing the stop words
    tokenizer = ToktokTokenizer()
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    filtered_tokens = [token for token in tokens if token not in stopword_list]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text

# convert emojis to words
def convert_emojis(text):
  for emot in UNICODE_EMO:
    text = text.replace(emot,' '.join(UNICODE_EMO[emot].replace(',','').replace(':','').replace('_',' ').split()))
  return text

#preprocessing function
def preprocessing(reviews):
    processed_reviews = reviews.copy()
    for i in range(len(reviews)):
        processed_reviews[i] = reviews[i].lower()
        processed_reviews[i] = remove_stopwords(processed_reviews[i])
        processed_reviews[i] = html_tag(processed_reviews[i])
        processed_reviews[i] = remove_sp(processed_reviews[i])
        processed_reviews[i] = convert_emojis(processed_reviews[i])
        processed_reviews[i] = con(processed_reviews[i])
    return(processed_reviews)

st.title('SENTIMENTAL ANALYSIS ON REVIEWS')
st.subheader("Enter the Product Name")
name = st.text_input("")

try : 
  if st.button('Confirm') or name is not None:
    dic = get_urls(name)
    keys = list(dic.keys())
    for i in range(5):
        st.write(keys[i])
        
    if st.checkbox('Show  some more Suggestions'):
        for i in range(len(keys)):
            if i >= 5:
                st.write(keys[i])

    try:
        st.subheader("Copy the perfect name of the product of your interest from the above list")
        new = st.text_input(" ")
        if st.button('Yes my interest is true') or new != '':
            reviews = get_reviews(dic, new)
            # preprocessing function
            processed_reviews = preprocessing(reviews)
            Analyze = SentimentIntensityAnalyzer()
            compound1 = []
            emoji = []
            for x in range(len(processed_reviews)):
                compound1.append(Analyze.polarity_scores(processed_reviews[x])['compound'])

            # emoji's appending
            for x in range(len(reviews)):
                if compound1[x] >= 0.8:
                    emoji.append('\U0001F600\U0001F600\U0001F600')
                elif compound1[x] < 0.8 and compound1[x] > 0.1:
                    emoji.append('\U0001F642\U0001F642')
                elif compound1[x] <= 0.1:
                    emoji.append('\U0001F611')

            # pd.options.display.max_colwidth = 100
            df1 = pd.DataFrame({'Reviews': reviews,
                                'Compound Score': compound1,
                                'Emojis': emoji})
            #pic = plt.imread(dic[new][1])
            col1, col2, col3 = st.beta_columns([1, 1, 1])
            col2.image(dic[new][1], caption=new, use_column_width = True)
    except KeyError:
        st.write("Copy the Product name properly")
except IndexError:
    st.write("Please enter the product name \U0001F642 \U0001F642")

print('Finished Processing\n')

try:
    col1, col2, col3 = st.beta_columns([0.1, 1, 0.01])
    if df1.empty:
        col2.write('Reviews Not Available')
    else:
        col2.dataframe(df1[0:5].style.set_properties(**{'text-align': 'center', 'color': 'black', 'background-color': 'white'}))

    if st.checkbox('Show all reviews'):
        col1, col2, col3 = st.beta_columns([0.1, 1, 0.01])
        if len(df1['Reviews']) >=5:
            col2.dataframe(df1[5:].style.set_properties(**{'background-color': 'white', 'color': 'black', 'text-align': 'center'}))
        else :
            col2.write("No more reviews available")
except:
    pass
