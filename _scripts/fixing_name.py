import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll", N=1000, rand=False)

for x in coder.obituaries:
    x._prop_spacyName()

"""
Faith Whitney Ziesing, a former trustee of Sarah Lawrence College, died of cancer last Friday at her home in Princeton, N.J. She was 75 years old.
[('the Pittsburgh Penguins', 41, 64, 'ORG'),
 ('the National Hockey League', 68, 94, 'ORG'),
 ('early today', 101, 112, 'DATE')]
 
 
Aldege Bastien, general manager of the Pittsburgh Penguins of the National Hockey League, died early today after his car collided with a motorcycle on a suburban highway.
[('Aldege Bastien', 0, 14, 'PERSON'),
 ('the Pittsburgh Penguins', 35, 58, 'ORG'),
 ('the National Hockey League', 62, 88, 'ORG'),
 ('early today', 95, 106, 'DATE')]

FOUND IT: Princess Masako


Chef Tell
['Chef Tell', 'Upper']
FS: The Philadelphia culinary legend known as Chef Tell, who gained nationwide fame as an early television chef in the 1970s and '80s, died Oct. 26 at his home in Upper Black Eddy, Pa.


(probably an easy fix... exclude because it's not a name)
['Havana']
FS: The blind Cuban pianist Frank Emilio Flynn, whose long career connected many tributaries of Cuban jazz, died Thursday at his home in Havana.
"""