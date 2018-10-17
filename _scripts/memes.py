from collections import Counter, defaultdict
import os
from csv import DictReader

import pandas as pd
from itertools import chain
import nlp
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

"""
Need to think of a more efficient way to do this.
We're looking for trends in counts of these substrings over time.

ALSO we're only interested in how many obits these show up in.

0.
GENERATE PLACEHOLDERS
    a. whenever he/she/name shows up, where it refers to the name of the person, replace it with <dead_person>
    b. dates with <date>
    c. companies with <company>
    d. names with <name>
    e. cities
    f. hospitals
    g. 

1.
DON'T RECORD SO MANY!
We can start by narrowing down the substrings to look at.
We want those which are not too uncommon.
That is, they must occur at least enough to see a trend
    (how much is that?)
    we have between 1000 and 3000 obits per year.
    a phrase is important if it occurs in at least 50 (100?) in any given year
    
so start by narrowing down the total counts (get rid of those which occur in less than 50 obits overall)
 
"""

if not os.path.exists("month_counts.pickle"):
    import occ

    # load the documents
    N = 3000

    coder = occ.Coder()
    coder.loadPreviouslyCoded("v2.0", N=N, rand=False)

    # sort them by date (why?)
    obits = sorted(coder.obituaries, key=lambda x: x['date'])

    # count the occurrence of tuples in months and years
    month_counter = defaultdict(Counter)
    year_counter = defaultdict(Counter)
    decade_counter = defaultdict(Counter)
    total_counter = Counter()

    for x in obits:
        tup = nlp.getTuples( nlp.word_tokenize(x['fullBody']), 3, 8 )

        d = x['date']
        mymonth = datetime(d.year, d.month, 1)
        myyear = datetime(d.year, 1, 1)
        mydecade = 10*(d.year // 10)

        month_counter[ mymonth ].update(tup)
        year_counter[ myyear ].update(tup)
        decade_counter[mydecade].update(tup)
        total_counter.update(tup)

    # establish a vocabulary satisfying some minimum # of words
    min_count = N * 0.01
    vocab = list(set( k for k in total_counter if total_counter[k] > min_count ))

    def variation(counter_collection, lowerbound=min_count):
        var = {k: np.array( [counter[k] for counter in counter_collection.values()] ).var()
               for k in vocab}
        return var

    def decade_variation(x):
        total = {k: sum(v) for k,v in decade_counter.items()}
        decades = {year:decade_counter[year][x] / total[year] for year in decade_counter}
        return np.array(list(decades.values())).var()

    vocab_str = [" ".join(x) for x in vocab]

    vm = variation(month_counter)
    stats = pd.DataFrame( data={
        "word":vocab_str,
        "var":[ vm[k] for k in vocab ],
        "count":[ total_counter[k] for k in vocab ]
    } )

    months = list(month_counter.keys())
    month_df = pd.DataFrame( data={
        "word":vocab_str*len(months),
        "count":[ month_counter[month][k] for month in months for k in vocab ],
        "month":months*len(vocab)
    } )

    stats.to_pickle("stats.pickle")
    month_df.to_pickle("month_counts.pickle")

    del month_counter
    del year_counter
    del total_counter

stats = pd.read_pickle("stats.pickle")
month_df = pd.read_pickle("month_counts.pickle")

# ok now that I have the data.... phew....

# plot yearly incidence of phrase
def plot_yearly(phrase):
    yearly = defaultdict(int)
    for m in month_df:
        if m['word'] != phrase:
            continue
        myyear = datetime(m['month'].year, 1, 1)
        yearly[ myyear ] += m['count']

    x = sorted(yearly.keys())
    y = [ yearly[z] for z in x ]

    plt.plot(x,y)

def plot_yearly(phrase):
    sub = month_df[ month_df['word'] == phrase ]
    plt.plot( sub['count'].resample("A") )

def var_yearly(phrase):
    sub = month_df[ month_df['word'] == phrase ]
    return sub['count'].resample("A").var()