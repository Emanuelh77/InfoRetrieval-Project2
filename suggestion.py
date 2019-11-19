import glob
import dask.dataframe as dd
from google.colab import files
import io
import sys
import os
import re
import collections


def process_recipies(filepath):
  global recipie_IDs

  with open(filepath) as fp:
    for cnt, line in enumerate(fp):
      try:
        line = line.rstrip('\n')
        tokens = line.split(",")
        recipie = tokens[0]
        recipie_id = int(tokens[1])

        if recipie in recipie_IDs.keys():
          recipie_IDs[recipie].append(recipie_id)
        else:
          recipie_IDs.update({recipie : [recipie_id]})
              
      except:
        print("bad recipie")

def process_reviews(filepath):
  global recipieIDs_avgRating

  with open(filepath) as fp:
    for cnt, line in enumerate(fp):
      try:
        line = line.rstrip('\n')
        tokens = line.split(",")
        recipie_id = int(tokens[1])
        rating = int(tokens[3])

        if recipie_id in recipieIDs_avgRating.keys():
          recipieIDs_avgRating[recipie_id].append(rating)
        else:
          recipieIDs_avgRating.update({recipie_id : [rating]})
              
      except:
        print("bad review")

  for recipie in recipieIDs_avgRating.keys():
    recipieIDs_avgRating[recipie] = sum(recipieIDs_avgRating[recipie]) / len(recipieIDs_avgRating[recipie])
	
	
def combine_recipies_ratings(recipies,ratings):
  global recipie_avgRating
  
  try:
    for recipie in recipies.keys():
      for ID in recipies[recipie]:
        if recipie in recipie_avgRating.keys():
          recipie_avgRating[recipie].append(ratings[ID])
        else:
          recipie_avgRating.update({recipie : [ratings[ID]]})
  except:
    print("no review for recipie")

  for recipie in recipie_avgRating.keys():
    recipie_avgRating[recipie] = sum(recipie_avgRating[recipie]) / len(recipie_avgRating[recipie])
        
def find_queries(query):
  query = query.lower()
  
  cq = {}
  for recipe in recipie_avgRating.keys():
    if query in recipe:
      cq.update({recipe : recipie_avgRating[recipe]})

  top5 = []
  for i in range(5):
    top5.append(max(cq, key=cq.get))
    del cq[max(cq, key=cq.get)]

  return top5

recipieIDs_avgRating = {}
recipie_IDs = {}
recipie_avgRating = {}

process_recipies(r'RAW_recipes.csv')
process_reviews(r'RAW_interactions.csv')
combine_recipies_ratings(recipie_IDs, recipieIDs_avgRating)
  
def suggest(q):
	return find-queries(q)
