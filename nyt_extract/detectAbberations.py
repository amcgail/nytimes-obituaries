# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 15:08:56 2017

@author: alec
"""

#detect abberations

from csv import reader, writer

inFn = "/home/alec/data projects/NYTIMESobituaries/extracted.noBody.nice.csv"
outFn = "/home/alec/data projects/NYTIMESobituaries/extracted.noBody.nice.abberations.csv"
with open(inFn) as inF:
    rs = reader(inF)
    with open(outFn, 'w') as outF:
        w = writer(outF)
        
        head = rs.next()
        w.writerow( head )
        
        for r in rs:
            abb = False
            
            name = r[ head.index("name") ]
            title = r[ head.index("title") ]
            
            if len( title.split("\n") ) > 1:
                abb = True
            if len( name.strip().split() ) < 2:
                abb = True
            if len( [c for c in name if c in "0123456789"] ) > 0:
                abb = True
                
            if abb:
                w.writerow( r )