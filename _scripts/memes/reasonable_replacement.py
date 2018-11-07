from csv import DictReader
from functools import partial
from operator import itemgetter

import occ
import nlp
from nlp import HumanName, isFullName
import numpy as np

debug_level = 0

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", N=10, rand=False)

ethnicities = ["Afghan", "Algerian", "Angolan", "Argentine", "Austrian", "Australian", "Bangladeshi", "Belarusian", "Belgian", "Bolivian", "Bosnian/Herzegovinian", "Brazilian", "British", "Bulgarian", "Cambodian", "Cameroonian", "Canadian", "Central African", "Chadian", "Chinese", "Colombian", "Costa Rican", "Croatian", "Czech", "Congolese", "Danish", "Ecuadorian", "Egyptian", "Salvadoran", "English", "Estonian", "Ethiopian", "Finnish", "French", "German", "Ghanaian", "Greek", "Guatemalan", "Dutch", "Honduran", "Hungarian", "Icelandic", "Indian", "Indonesian", "Iranian", "Iraqi", "Irish", "Israeli", "Italian", "Ivorian", "Jamaican", "Japanese", "Jordanian", "Kazakh", "Kenyan", "Lao", "Latvian", "Libyan", "Lithuanian", "Malagasy", "Malaysian", "Malian", "Mauritanian", "Mexican", "Moroccan", "Namibian", "New Zealand", "Nicaraguan", "Nigerien", "Nigerian", "Norwegian", "Omani", "Pakistani", "Panamanian", "Paraguayan", "Peruvian", "Philippine", "Polish", "Portuguese", "Congolese", "Romanian", "Russian", "Saudi, Saudi Arabian", "Scottish", "Senegalese", "Serbian", "Singaporean", "Slovak", "Somalian", "South African", "Spanish", "Sudanese", "Swedish", "Swiss", "Syrian", "Thai", "Tunisian", "Turkish", "Turkmen", "Ukranian", "Emirati", "American", "Uruguayan", "Vietnamese", "Welsh", "Zambian", "Zimbabwean"]

with open("world-cities_csv.csv", 'r') as wc:
    cities = list(map(itemgetter("name"), DictReader(wc)))
    cities = sorted(cities, key=lambda x: -len(x))

with open("world-universities.csv", 'r') as wc:
    unis = list(map(itemgetter("name"), DictReader(wc)))
    unis = sorted(unis, key=lambda x: -len(x))

for obit in coder.obituaries:
    tokenized = nlp.tokenize_name( full_body=obit['fullBody'], name=obit['name'] )
    tokenized = nlp.tokenize_list_as(tokenized, unis, "<university>")
    tokenized = nlp.tokenize_list_as( tokenized, cities, "<city>" )
    tokenized = nlp.tokenize_list_as( tokenized, ethnicities, "<ethnicity>")

    print(obit['fullBody'])
    for i in range(3):
        print("-----------")
    print(tokenized)
    for i in range(3):
        print("-----------")