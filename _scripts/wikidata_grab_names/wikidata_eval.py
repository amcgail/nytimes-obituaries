from csv import DictReader

with open('Governors.csv', 'r') as govf:
	govs = list( DictReader( govf ) )
	govNames = [ x['Full Name'] for x in govs ]
	govNames = filter( lambda x: x.strip() != "", govNames )
	govNames = [ x[5:] for x in govNames ]
	govNames = [ x.split(",")[0].split()[-1] for x in govNames ]

with open('wiki_govs.csv','r') as govf:
	wgovs = list( DictReader( govf ) )
	wgovs = set( x['name'] for x in wgovs )
	wgovs = [ x.split(",")[0].split()[-1] for x in wgovs ]

for gov in govNames:
	if not gov in wgovs:
		print( gov )
