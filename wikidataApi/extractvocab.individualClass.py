# -*- coding: utf-8 -*-
import urllib
import json

from collections import Counter

from nltk import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import RidgeClassifierCV
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score

from sklearn.preprocessing import MultiLabelBinarizer

import csv
import sys
from os import path
#sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )
#from lib import *

inFn = path.join( path.dirname(__file__), "lookthemallup.wiki.txt" )
csv.field_size_limit(500 * 1024 * 1024)

vectorizer = TfidfVectorizer(use_idf=False, norm=None, max_df=0.5, min_df=10,
                     stop_words=None, ngram_range=(1,2))
results = CountVectorizer()

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
            l['first500'],
            json.loads( l['words'] )
        ] )
        #indicators = 
        #indicated = 

mlb = MultiLabelBinarizer()
Y_enc = mlb.fit_transform( [x[1] for x in data] )
X = vectorizer.fit_transform( [x[0] for x in data] )
ncase, nfeat = X.shape

X_train = X[:int(0.9*ncase),]
Y_enc_train = Y_enc[:int(0.9*ncase),]

X_test = X[int(0.9*ncase):,]
Y_enc_test = Y_enc[int(0.9*ncase):,]

#Y = results.fit_transform( [" ".join( x[1] ) for x in data])

import random

perClass = np.sum( Y_enc, 0 )
largeOnes, = np.where( perClass > 20 )

allwords = vectorizer.get_feature_names()

f1hist = []

#get words associated with "writer"
for i in largeOnes:

    classifier = LinearSVC()
    classifier.fit(X_train, Y_enc_train[:,i])
    
    f1= f1_score( classifier.predict(X_test), Y_enc_test[:,i])
    
    if f1 > 0.4:
        print(
            mlb.classes_[i], 
            "[F1: %0.4f, correct: %0.3f%%, percent true 0s: %0.3f%%]" %
            (f1, 100*classifier.score(X_test, Y_enc_test[:,i]), 100*np.count_nonzero(1-Y_enc_test[:,i]) / np.shape(Y_enc_test[:,i])[0] )
        )
        
        co = classifier.coef_[0]
        wordsi = co.argsort()[-10:]
        words = [ allwords[x] for x in wordsi ]
        
        #print(mlb.classes_[i])
        print(", ".join( [ "%s (%0.1f)"%(allwords[x],co[x]) for x in wordsi[::-1][:5]] ))
        print("")
        
    f1hist.append(f1)

"""
NOT TOO BAD!

American football player [F1: 0.6154, correct: 98.355%, percent true 0s: 97.204%]
football (3.2), bowl (1.7), football league (1.5), super (1.4), national football (1.3)

actor [F1: 0.7250, correct: 92.763%, percent true 0s: 85.197%]
actor (4.8), actress (3.5), films (2.2), actor who (1.7), television (1.7)

artist [F1: 0.7599, correct: 81.086%, percent true 0s: 60.197%]
actor (3.2), jazz (2.6), painter (2.5), composer (2.4), artist (2.2)

composer [F1: 0.5152, correct: 94.737%, percent true 0s: 92.434%]
composer (5.0), music (2.6), songwriter (2.3), songs (2.1), composers (1.6)

film actor [F1: 0.6250, correct: 94.079%, percent true 0s: 90.296%]
actor (3.7), actress (2.1), films (2.1), actor who (1.8), role (1.6)

gridiron football player [F1: 0.6154, correct: 98.355%, percent true 0s: 97.204%]
football (3.2), bowl (1.7), football league (1.5), super (1.4), national football (1.3)

ice hockey player [F1: 0.6667, correct: 99.342%, percent true 0s: 98.684%]
hockey (2.8), national hockey (1.3), hockey league (1.2), rangers (0.9), the rangers (0.8)

jazz musician [F1: 0.5600, correct: 98.191%, percent true 0s: 97.862%]
jazz (5.2), ellington (1.6), saxophonist (1.4), trumpeter (1.4), composer (1.1)

mathematician [F1: 0.5714, correct: 99.507%, percent true 0s: 99.178%]
mathematician (2.8), mathematics (2.3), mathematician who (1.6), computer (1.4), of mathematics (1.2)

musician [F1: 0.7051, correct: 92.434%, percent true 0s: 85.855%]
music (3.6), composer (3.5), singer (3.5), jazz (3.0), band (2.8)

politician [F1: 0.5439, correct: 91.447%, percent true 0s: 88.816%]
minister (2.5), senator (1.8), governor (1.7), union (1.7), congress (1.6)

singer [F1: 0.5106, correct: 96.217%, percent true 0s: 94.901%]
singer (4.2), singing (2.6), soprano (2.3), voice (2.1), songs (1.7)

visual artist [F1: 0.5195, correct: 93.914%, percent true 0s: 91.118%]
painter (3.2), photographer (3.1), artist (2.8), sculptor (2.5), abstract (1.9)

vocalist [F1: 0.5106, correct: 96.217%, percent true 0s: 94.901%]
singer (4.2), singing (2.6), soprano (2.3), voice (2.1), songs (1.7)

writer [F1: 0.6480, correct: 81.414%, percent true 0s: 69.243%]
writer (2.7), journalist (2.6), author (2.5), critic (2.3), novels (2.3)

"""