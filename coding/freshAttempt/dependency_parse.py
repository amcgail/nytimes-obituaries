# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# =============================================================================
# Possible next steps:
#     + Create classes as containers for functions
#     + More library classes to the library folder and import them
# =============================================================================

from os import path
import sys
from collections import Counter

basedir = path.join( path.dirname(__file__), '..', ".." )
sys.path.append( path.join( basedir, 'lib' ) )
import occ

sCount = Counter()
#mycoder.loadPreviouslyCoded("bagOfWords10000")

i = int( sys.argv[1] )
print( "DOING %s" % i )

mycoder = occ.Coder()
mycoder.loadDocs(start=10000 * i, N=10000, rand=False)
mycoder.codeAll(["guess"])
mycoder.dumpCodes("codingAll_%s" % i)
