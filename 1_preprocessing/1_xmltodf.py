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



countermissingtitle=0
counternotdeutschsprachig=0
i=0


with open('dnb_all_dnbmarc_20221013-1.mrc.xml', 'rb') as f, open('converted/dnb_all_dnbmarc_20221013-1.csv', 'w', newline='', encoding='utf-8') as csvfile:
  writer = csv.writer(csvfile)
  writer.writerow(['id', 'leader', 'fixedlength008', 'isbn', 'ddc', 'other_ddc', 'belletristik', 'lang_code', 'translated_lang_code', 'deutschsprachig', 'uebersetzung', 'laendercode', 'extraauthorfield',  'allauthorsdictstring', 'added_author_titles', 'added_titles', 'title', 'subtitle', 'titlesubtitle', 'pubyear', 'pubyear_old', 'pubyear_erstauflage_008', 'pubyear_neuauflage_008', 'istneuauflage', 'auflage', 'keywords', 'keywords2', 'zeitschlagwort', 'geografika', 'keywords_form', 'nebeneintragung'])

  for _, record in etree.iterparse(f, tag='{http://www.loc.gov/MARC21/slim}record', encoding='utf-8'):
    leader = record.findall(".//{http://www.loc.gov/MARC21/slim}leader")
    leader = process_field(leader)

    id = record.findall(".//{http://www.loc.gov/MARC21/slim}controlfield[@tag='001']")
    id = process_field(id)
    
    fixedlength008 = record.findall(".//{http://www.loc.gov/MARC21/slim}controlfield[@tag='008']")
    fixedlength008 = process_field(fixedlength008)
    
    isbn = record.findall(".//{http://www.loc.gov/MARC21/slim}controlfield[@tag='020']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    isbn = process_field(isbn)
      
    ddc = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='082']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    ddc = process_field(ddc)
    
    belletristik = "B" in ddc

    other_ddc = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='084']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    other_ddc = process_field(other_ddc)
    
    lang_code = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='041']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    lang_code = process_field(lang_code)
    
    translated_lang_code = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='041']//{http://www.loc.gov/MARC21/slim}subfield[@code='h']")
    translated_lang_code = process_field(translated_lang_code)
    
    deutschsprachig = "ger" in lang_code
    uebersetzung = "ger" not in translated_lang_code and translated_lang_code!=""
    
    laendercode = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='044']//{http://www.loc.gov/MARC21/slim}subfield[@code='c']")
    laendercode = process_field(laendercode)
    
    
    #get author information
    author_info = {}

    author_fields = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='100']")

    # Iterate over each 100 field
    for field in author_fields:
      # Extract the author's name
      author_name = field.findall(".//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
      author_name = process_field(author_name)
    
      # Extract the author's role
      author_role = field.findall(".//{http://www.loc.gov/MARC21/slim}subfield[@code='4']")
      author_role = process_field(author_role)
    
      # Extract the author's GND
      author_gnd = field.findall(".//{http://www.loc.gov/MARC21/slim}subfield[@code='0']")
      author_gnd = process_field(author_gnd)
      
      if 'd-nb.info/gnd/' in author_gnd:
        author_gnd_preprocessed = re.sub(r'd-nb.info/gnd/',"",re.search(r'd-nb.info/gnd/\d+(-?\d*X*)+', author_gnd).group())
      else: 
        author_gnd_preprocessed = ""
    
      # Extract the author's Lebensdaten
      author_lebensdaten = field.findall(".//{http://www.loc.gov/MARC21/slim}subfield[@code='d']")
      author_lebensdaten = process_field(author_lebensdaten)

      if '-' in author_lebensdaten:
        date_parts = author_lebensdaten.strip().split("-") 
        birth_year = date_parts[0]
        death_year = date_parts[1]
      else:
        birth_year, death_year = "", ""
    
      # Check if the author has already been added to the dictionary
      if author_name not in author_info:
        author_info[author_name] = {
            'role': author_role,
            'author_gnd': author_gnd,
            'author_gnd_preprocessed': author_gnd_preprocessed,
            'author_lebensdaten': author_lebensdaten,
            'author_birth_year': birth_year,
            'author_death_year': death_year,
        }
    
    authorinfostring = str(author_info)
  
    extraauthorfield = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='245']//{http://www.loc.gov/MARC21/slim}subfield[@code='c']")
    extraauthorfield = process_field(extraauthorfield)
    
    #get added author information
    added_author_info = {}
    added_author_fields = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='700']")

    for field in added_author_fields:
      added_author_name = field.findall(".//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
      added_author_name = process_field(added_author_name)
    
      added_author_role = field.findall(".//{http://www.loc.gov/MARC21/slim}subfield[@code='4']")
      added_author_role = process_field(added_author_role)
    
      added_author_gnd = field.findall(".//{http://www.loc.gov/MARC21/slim}subfield[@code='0']")
      added_author_gnd = process_field(added_author_gnd)
      
      if 'd-nb.info/gnd/' in added_author_gnd:
        added_author_gnd_preprocessed = re.sub(r'd-nb.info/gnd/',"",re.search(r'd-nb.info/gnd/\d+(-?\d*X*)+', added_author_gnd).group())
      else: 
        added_author_gnd_preprocessed = ""
    
      added_author_lebensdaten = field.findall(".//{http://www.loc.gov/MARC21/slim}subfield[@code='d']")
      added_author_lebensdaten = process_field(added_author_lebensdaten)
      
      if '-' in added_author_lebensdaten:
        date_parts = added_author_lebensdaten.strip().split("-") 
        birth_year = date_parts[0]
        death_year = date_parts[1]
      else:
        birth_year, death_year = "", ""
    
      # Check if the author has already been added to the dictionary
      if added_author_name not in added_author_info:
        added_author_info[added_author_name] = {
            'role': added_author_role,
            'author_gnd': added_author_gnd,
            'author_gnd_preprocessed': added_author_gnd_preprocessed,
            'author_lebensdaten': added_author_lebensdaten,
            'author_birth_year': birth_year,
            'author_death_year': death_year,
        }
    
    added_authorinfostring = str(added_author_info)
    
    #all authors in a dictionary and the latter is the winner
    allauthorsdict = added_author_info.copy()
    allauthorsdict.update(author_info)
    allauthorsdictstring = str(allauthorsdict)

    added_author_titles = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='700']//{http://www.loc.gov/MARC21/slim}subfield[@code='t']")
    added_author_titles = process_field(added_author_titles)

    added_titles = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='776']//{http://www.loc.gov/MARC21/slim}subfield[@code='t']")
    added_titles = process_field(added_titles)
    
    title = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='245']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    title = process_field(title)
    
    subtitle = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='245']//{http://www.loc.gov/MARC21/slim}subfield[@code='b']")
    subtitle = process_field(subtitle)
    
    titlesubtitle = title + subtitle
    
    pubyear = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='264']//{http://www.loc.gov/MARC21/slim}subfield[@code='c']")
    pubyear = process_field(pubyear)

    auflage = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='250']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    auflage = process_field(auflage)
    
    pubyear_old = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='260']//{http://www.loc.gov/MARC21/slim}subfield[@code='c']")
    pubyear_old = process_field(pubyear_old)
    
    keywords = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='650']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    keywords = process_field(keywords)
    
    keywords2 = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='653']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    keywords2 = process_field(keywords2)  
    
    zeitschlagwort = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='648']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    zeitschlagwort = process_field(zeitschlagwort)  
    
    geografika = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='651']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    geografika = process_field(geografika)  
    
    keywords_form = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='655']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    keywords_form = process_field(keywords_form)
    
    nebeneintragung = record.findall(".//{http://www.loc.gov/MARC21/slim}datafield[@tag='688']//{http://www.loc.gov/MARC21/slim}subfield[@code='a']")
    nebeneintragung = process_field(nebeneintragung)
    
    #220116r20221947gw |||||o|||| 00||||ger
    pubyear_erstauflage_008 = fixedlength008[7:11]
    pubyear_neuauflage_008 = fixedlength008[11:15]
    
    istneuauflage = pubyear_neuauflage_008!="9999" and pubyear_neuauflage_008!="" 
    
    if titlesubtitle=="": 
      countermissingtitle += 1
    if not deutschsprachig: 
      counternotdeutschsprachig += 1
  
    #if author!="" and titlesubtitle!="" and deutschsprachig and isauthor and not hasmultipleauthors:
    if titlesubtitle!="" and deutschsprachig:
      writer.writerow([id, leader, fixedlength008, isbn, ddc, other_ddc, belletristik, lang_code, translated_lang_code, deutschsprachig, uebersetzung, laendercode, extraauthorfield, allauthorsdictstring, added_author_titles, added_titles, title, subtitle, titlesubtitle, pubyear, pubyear_old, pubyear_erstauflage_008, pubyear_neuauflage_008, istneuauflage, auflage, keywords, keywords2, zeitschlagwort, geografika, keywords_form, nebeneintragung])
    
    i+=1
    print(i)
    record.clear()


print(countermissingtitle)
print(counternotdeutschsprachig)

#repeat this for all 5 marc parts
