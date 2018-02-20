# -*- coding: utf-8 -*-
import urllib
import json

from collections import Counter

from nltk import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import RidgeClassifierCV

from sklearn.preprocessing import MultiLabelBinarizer

import csv
import sys
from os import path
#sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )
#from lib import *

inFn = path.join( path.dirname(__file__), "lookthemallup.wiki.txt" )
csv.field_size_limit(500 * 1024 * 1024)

vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5, min_df=10,
                     stop_words='english', ngram_range=(1,1))
results = CountVectorizer()

classifier = RidgeClassifierCV()

with open(inFn) as inF:
  
    data = []  
  
    for l in csv.DictReader(inF):
        
        sentences = sent_tokenize(l['first500'])
        
        if len(sentences) < 2:
            print("skipping(tooFewSentences)", l['fn'])
            continue
        
        firstSentence = sentences[0].strip()
        firstSentence = " ".join( firstSentence.split() )
        
        if "," not in firstSentence:
            firstSentence += " " + " ".join( sentences[1].strip().split() )
            
        firstSentence = firstSentence.strip()
        if len(firstSentence) < 5:
            continue
        
        data.append( [
            firstSentence,
            json.loads( l['words'] )
        ] )
        #indicators = 
        #indicated = 
    
if False:    
    labelCounter = Counter()
    for x in data:
        labelCounter.update(x[1])
        
    removeFromAll = set()    
        
    for k, v in labelCounter.items():
        if v > 0.1 * len(data):
            removeFromAll.add( k )
    
    for i, x in enumerate(data):
        data[i][1] = [ y for y in x[1] if y not in removeFromAll ]
        if len(data[i][1]) == 0:
            data[i][1] = x[1]

mlb = MultiLabelBinarizer()
Y_enc = mlb.fit_transform( [x[1] for x in data] )

X_train = vectorizer.fit_transform( [x[0] for x in data] )
#Y = results.fit_transform( [" ".join( x[1] ) for x in data])

classifier.fit(X_train, Y_enc)#Y.todense())

import random

perClass = np.sum( Y_enc, 0 )
largeOnes, = np.where( perClass > 10 )

allwords = vectorizer.get_feature_names()

#get words associated with "writer"
random.shuffle(largeOnes)
for i in largeOnes[:10]:
    co = classifier.coef_[i,:]
    wordsi = co.argsort()[-10:]
    words = [ allwords[x] for x in wordsi ]
    
    print(mlb.classes_[i])
    print([ (allwords[x], "%0.3f"%co[x]) for x in wordsi] )

failConfidence = []
succConfidence = []
fail= 0
succ = 0

for i in range( X_train.shape[0] ):
    if i % 100 == 0:
        print( "processed", i )
        
    prediction = classifier.predict(X_train[i,:])
    prediction_name = mlb.classes_[prediction[0]]
    reality = data[i][1]
    
    best_confidence = np.max( classifier.decision_function(X_train[i,:]) )
    
    print(prediction_name, reality)
    
    if prediction_name not in reality:
        fail += 1
        failConfidence.append(best_confidence)
    else:
        succ += 1
        succConfidence.append(best_confidence)

"""
for i in range( X_train.shape[0] )[:100]:
    prediction = classifier.predict(X_train[i,:])
    prediction_name = mlb.classes_[prediction]
    reality = data[i][1]
    
    print(prediction_name, reality)
    print( np.max( classifier.decision_function(X_train[i,:]) ) )
"""

fig, axs = plt.hist( failConfidence, 30 )
fig, axs = plt.hist( succConfidence, 30 )

x = np.arange(-1, 1, 0.1)
def falsePositives(p):
    return len( np.where( np.array(failConfidence) > p )[0] ) / len(failConfidence)
def falseNegatives(p):
    return len( np.where( np.array(succConfidence) < p )[0] ) / len(succConfidence)
falsePositives = np.vectorize(falsePositives)
falseNegatives = np.vectorize(falseNegatives)

