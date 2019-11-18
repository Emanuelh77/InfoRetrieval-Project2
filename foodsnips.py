#!/usr/bin/env python
# coding: utf-8

# In[11]:


import ast
import pandas as pd
import math
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer


# In[ ]:





# In[2]:


lemmatizer = WordNetLemmatizer()
stops = stopwords.words('english')
coll_stops = ["prepare", "course", "dietary", "easy", "pepper", "recipe", "salt"]
stops.extend(coll_stops)
ps = PorterStemmer()


# In[ ]:





# In[9]:


index_food_tfidf = pd.read_csv('new_food_tfidfindex.csv', names=["word", "tfidf"])
index_food_tfidf["tfidf"] = [ast.literal_eval(x) for x in index_food_tfidf.tfidf]
data_combined = pd.read_csv('new_recipes.csv')


# In[ ]:





# In[6]:


def clean(doc):
    doc_low = doc.lower().replace("–", " ")
    words = word_tokenize(doc_low)
    words = [lemmatizer.lemmatize(w).strip() for w in words if not w in stops and w.isalpha()]
    words = [ps.stem(w) for w in words]
    return words


# In[7]:


def snippet (doc_id, q):
    sent_doc = pd.DataFrame()
    cosine_df = pd.DataFrame()
    
    #Grab Full doc from corpus, since I dont keep periods
    doc = data_combined.loc[data_combined.index == doc_id, 'content'].item()
    
    #Tokenize into sentences and clean
    sent_doc['sent'] = sent_tokenize(doc)
    sent_doc['clean'] = [clean(x) for x in sent_doc.sent]
    
    #Create vector from query and sentence
    cosine = []
    for x in sent_doc.clean:
        x_set = set(x)
        q_set = set(q_c)
        vector = x_set.union(q_set)
    
    #Calculate vectore values for both
        q_v = []
        s_v = []
        for w in vector:
            if w in q_set:
                q_v.append(index_food_tfidf.loc[index_food_tfidf.word == w]['tfidf'].item()[doc_id])
            else:
                q_v.append(0)
            if w in x_set:
                s_v.append(index_food_tfidf.loc[index_food_tfidf.word == w]['tfidf'].item()[doc_id])
            else:
                s_v.append(0)
    
    #Calcumate cosine simularity
        c = 0
        for i in range(len(vector)):
            c += q_v[i] * s_v[i]
        cosine.append(c / math.sqrt((math.pow(sum(q_v), 2)) * (math.pow(sum(s_v), 2))))
    cosine_df['sim'] = cosine
    cosine_df = cosine_df.sort_values(by=['sim'], ascending =False).reset_index()
    sent_pos = list(cosine_df[0:3]['index'])
    

    snip = []
    snip.append(data_combined.name[doc_id])
    for x in sent_pos:
        snip.append(sent_doc.sent[x])
    return snip


# In[ ]:




