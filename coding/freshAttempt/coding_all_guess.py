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

mycoder = occ.Coder()
mycoder.loadPreviouslyCoded("codingAll")
mycoder.codeAll(["guess"])
mycoder.dumpCodes("codingAll")
