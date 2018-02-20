# -*- coding: utf-8 -*-

import gensim, logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from os import sys, path
import csv
from csv import DictReader
from nltk import sent_tokenize

basedir = path.join( path.dirname(__file__), '..', ".." )
sys.path.append( path.join( basedir, 'lib' ) )

from lib import *

inFn = path.join( basedir, "data","extracted.all.nice.csv" )
csv.field_size_limit(500 * 1024 * 1024)

sentences = []

with open(inFn) as inF:
    rs = DictReader(inF)
    
    n = 0
    for r in rs:
        n+=1
        if n > 1000:
            break
        
        sentences += [ word_tokenize(x) for x in sent_tokenize(r['fullBody']) ]
        
model = gensim.models.Word2Vec(sentences, min_count=1)