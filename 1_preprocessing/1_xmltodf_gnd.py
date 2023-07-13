from lxml import etree
import csv
import pandas as pd
import re


def process_field(field):
  if len(field) == 0:
    return ""
  else:
    result_list = []
    for i, element in enumerate(field):
      if i == 0:
        result_list.append(element.text)
      elif element.getparent() == field[i-1].getparent():
        result_list[-1] += ";" + element.text
      else:
        result_list.append(element.text)
    return "|".join(result_list)


i=0
with open('authorities-gnd-person_dnbmarc_20221013.mrc.xml', 'rb') as f, open('converted/dnbmarc-gnd-person_20221013.csv', 'w', newline='', encoding='utf-8') as csvfile:
  writer = csv.writer(csvfile)
  writer.writerow(['id_gnd', 'leader', 'shouldbepiz', 'author', 'author_lebensdaten', 'birth_year', 'death_year', 'author_furthernames', 'author_added', 'author_added_lebensdaten'])
  
  for _, record in etree.iterparse(f, tag='{http://www.loc.gov/MARC21/slim}record', encoding='utf-8'):
    leader = record.findall(".//{http://www.loc.gov/MARC21/slim}leader")
    leader = process_field(leader)
    
    id_gnd = record.findall(".//{http://www.loc.gov/MARC21/slim}controlfield[@tag='001']")
    id_gnd = process_field(id_gnd)
    #this id can be merged with 100;0 -> author_gnd_preprocessed
    #if id is not available in the bib catalogue, i need to merge on the name
    
    author = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='100']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    author = process_field(author)
    
    #lastname, firstname = author.split(", ")
    #author_named = firstname + " " + lastname
    
    author_lebensdaten = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='100']//{http://www.loc.gov/MARC21/slim}subfield[@code='d']")
    author_lebensdaten = process_field(author_lebensdaten)
    
    if '-' in author_lebensdaten:
      date_parts = author_lebensdaten.strip().split("-") 
      birth_year = date_parts[0]
      death_year = date_parts[1]
    else:
      birth_year, death_year = "", ""
    
    shouldbepiz = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='075']//{http://www.loc.gov/MARC21/slim}subfield[@code='b']")
    shouldbepiz = process_field(shouldbepiz)
    
    author_furthernames = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='400']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    author_furthernames = process_field(author_furthernames)
      
    #this should not contain additional info
    author_added = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='700']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    author_added = process_field(author_added)
    
    author_added_lebensdaten = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='700']//{http://www.loc.gov/MARC21/slim}subfield[@code='d']")
    author_added_lebensdaten = process_field(author_added_lebensdaten)
    
    #gender = record.findall(".//{http://www.loc.gov/MARC21/slim}controlfield[@tag='375']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    #gender = process_field(gender)
    
    #language = record.findall(".//{http://www.loc.gov/MARC21/slim}controlfield[@tag='377']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    #language = process_field(language)
    
    writer.writerow([id_gnd, leader, shouldbepiz, author, author_lebensdaten, birth_year, death_year, author_furthernames, author_added, author_added_lebensdaten])
    
    i+=1
    print(i)
    record.clear()

print("OK")
