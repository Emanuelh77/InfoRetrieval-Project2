import pandas as pd
import numpy as np
import math
import json
import ast
import yaml
import operator

from numba import jit, cuda
from itertools import combinations
from collections import Counter as ctr
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

idf_df = pd.read_csv('idf.csv')

max_d = pd.read_csv('max_d.csv')
max_d = max_d.rename(columns={'Unnamed: 0': 'DocID'})

index = pd.read_csv('index.csv', names=['word', 'frequency'])

#data = pd.read_csv('wikipedia_text_files.csv')
#cd = pd.read_csv('doc_df.csv')


lemmatizer = WordNetLemmatizer()
stops = stopwords.words('english')
coll_stops = ["also", "first", "one", "new", "year", "two", "time", "state", "school"]
stops.extend(coll_stops)

def clean(doc):
    doc_low = doc.lower().replace("–", " ")
    words = word_tokenize(doc_low)
    words = [lemmatizer.lemmatize(w).strip() for w in words if not w in stops and wordnet.synsets(w) and w.isalpha()]
    return words

def get_candidate_resources(query):
    clean_query = clean(query)
    CR = []
    word_key_list = []
    if len(clean_query) == 1:
        only_word = clean_query[0]    #sw = single word
        sw_dict = yaml.load(index.loc[index.word == only_word, 'frequency'].item())
        CR.extend(list(sw_dict.keys()))
        if len(CR) > 50:
            return CR[:50]
        else: return CR
    for w in clean_query:
        w_dict = yaml.load(index.loc[index.word == w, 'frequency'].item())
        word_key_list.append(list(w_dict.keys()))
    CR.extend(set(word_key_list[0]).intersection(*word_key_list[1:]))
    if len(clean_query) == 2:
        if len(CR)<50:
            first_list = []
            second_list = []
            first_word = clean_query[0]
            second_word = clean_query[1]
            first_dict = yaml.load(index.loc[index.word == first_word, 'frequency'].item())
            second_dict = yaml.load(index.loc[index.word == second_word, 'frequency'].item())
            first_list.append(first_dict.keys())
            second_list.append(second_dict.keys())
            CR.extend(first_list)
            CR.extend(second_list)
            if len(set(CR))>50:
                return CR[:50]
            else: return set(CR)
        else:
            if len(CR) > 50:
                return CR[:50]
            else:
                return CR
    elif len(CR)<50:     #if the list of candidate resources is less than 50
        combs = combinations(clean_query, len(query)-1)     #use n-1 terms from the query
        for comb in list(combs):        #for combination in combinations
            word_key_list = []
            for w in list(comb):        #for word in n-1 combination
                w_dict = yaml.load(index.loc[index.word == w, 'frequency'].item())
                word_key_list.append(list(w_dict.keys()))
            CR.extend(set(word_key_list[0]).intersection(*word_key_list[1:])) #find the intersection between all n-1 query terms
            CR = set(CR)
            if len(set(CR))<50:
                continue
            elif len(set(CR))>50:
                CR = set(CR)[:49]
                break
            else: break
    return CR[:50]

def idf(w):
    idf_value = idf_df.loc[idf_df.word==w, 'idf'].item()
    return int(idf_value)

def frequency(w,d):
    word_freq_dict = yaml.load(index.loc[index.word == w, 'frequency'].item())
    word_freq = word_freq_dict[d]
    return int(word_freq)

def term_freq(w,d):
    max_showing_word = int(max_d.loc[max_d.DocID == d, 'max_d'].item())
    return frequency(w,d)/max_showing_word

def relevance_ranking(q, cand_resources):
    clean_query = clean(q)
    rel_docs = {}
    for d in cand_resources:
        rel_score = 0
        if len(clean_query)==1:
            w = clean_query[0]
            result = term_freq(w,d) * idf(w)
            rel_docs[d] = result
        elif len(clean_query)>1:
            for word in clean_query:
                result = term_freq(word,d) * idf(word)
                rel_score += result
            rel_docs[d] = rel_score
    sorted_rel_docs = sorted(rel_docs.items(), key=operator.itemgetter(1), reverse=True)
    results = [i[0] for i in sorted_rel_docs[:5]]
    return results

query = 'sven'
r = get_candidate_resources(query)

# Takes one document and creates a list containing the title a top 3 related sentence to a given clean query
# def snippet(doc_id, q):
#     doc_tfidf = pd.DataFrame()
#     sent_doc = pd.DataFrame()
#     cosine_df = pd.DataFrame()
#     sent_doc_c = pd.DataFrame()
#
#     # Create Frame with TF-IDF for every word in the clean doc
#     clean_list = ast.literal_eval(cd.clean[doc_id])
#     doc_tfidf['words'] = list(set(clean_list))
#     doc_tfidf['tf-idf'] = [
#         (ast.literal_eval(index.loc[index.word == x, 'frequency'].item()).get(doc_id) / max_d.max_d[doc_id]) * idf_df.loc[
#             idf_df.word == x, 'idf'].item() for x in doc_tfidf.words]
#
#     # Grab Full doc from corpus, since I dont keep periods
#     doc = data.loc[cd.index == doc_id, 'content'].item()
#
#     # Tokenize into sentences and clean
#     sent_doc['sent'] = sent_tokenize(doc)
#     sent_doc['clean'] = [clean(x) for x in sent_doc.sent]
#     sent_doc_c = sent_doc[sent_doc.astype(str)['clean'] != '[]'].reset_index()
#
#     # Create vector from query and sentence
#     cosine = []
#     for x in sent_doc_c.clean:
#         x_set = set(x)
#         q_set = set(q)
#         vector = x_set.union(q_set)
#
#         # Calculate vectore values for both
#         q_v = []
#         s_v = []
#         for w in vector:
#             if w in q_set:
#                 q_v.append(doc_tfidf.loc[doc_tfidf.words == w, 'tf-idf'].item())
#             else:
#                 q_v.append(0)
#             if w in x_set:
#                 s_v.append(doc_tfidf.loc[doc_tfidf.words == w, 'tf-idf'].item())
#             else:
#                 s_v.append(0)
#
#         # Calcumate cosine simularity
#         c = 0
#         for i in range(len(vector)):
#             c += q_v[i] * s_v[i]
#         cosine.append(c / math.sqrt((math.pow(sum(q_v), 2)) * (math.pow(sum(s_v), 2))))
#     cosine_df['sim'] = cosine
#     cosine_df = cosine_df.sort_values(by=['sim'], ascending=False).reset_index()
#     sent_pos = list(cosine_df[0:3]['index'])
#
#     # Put together the snippet as a list to return
#     snip = []
#     para = ""
#     snip.append(data.title[doc_id])
#     for x in sent_pos:
#         para = para + sent_doc_c.sent[x]
#     snip.append(para)
#     return snip