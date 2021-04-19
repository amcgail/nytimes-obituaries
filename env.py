from os import path
from os.path import exists, join

possible_home_dirs = [
    "C:/Users/Alec McGail",
    "/home/alec",
    "C:/Users/amcga",
	"C:/Users/Public"
]

homeDir = None
for d in possible_home_dirs:
    if exists(join(d,'codeDumps')):
        homeDir = d

if homeDir is None:
    raise Exception("No valid home directory found")

codeDumpDir = join( homeDir, "codeDumps" )