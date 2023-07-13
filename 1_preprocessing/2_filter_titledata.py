import csv
import pandas as pd
import re


with open('converted/dnb_all_dnbmarc_20221013-5.csv', 'r', encoding='utf-8') as infile, open('converted/dnb_all_dnbmarc_20221013-5_filtered.csv', 'w', newline='', encoding='utf-8') as outfile:
  reader = csv.DictReader(infile)
  fieldnames = reader.fieldnames + ['aut_authorname', 'aut_author_gnd', 'aut_author_gnd_preprocessed', 'aut_author_lebensdaten',  'aut_author_birth_year', 'aut_author_death_year', 'author_named', 'authorname_birth_year', 'authorname_death_year']
  
  writer = csv.DictWriter(outfile, fieldnames=fieldnames)
  writer.writeheader()
  
  counternoauthor = 0
  countermultipleauthors = 0
  countersammlung = 0
  countersammlungstrich = 0
  countersammlungaddedtitles = 0
  countersoftware = 0
  counternoyear = 0
  counterhrsginauthor = 0
  i=0
  
  for row in reader:
    
    leader = row['leader']
    field008 = row['fixedlength008'] 
    
    pubyear = row['pubyear']
    
    auflage = row['auflage']
    pubyear_erstauflage_008 = field008[7:11]
    pubyear_neuauflage_008 = field008[11:15]
    
    allauthorsdictstring = row['allauthorsdictstring']
    allauthorsdict = eval(allauthorsdictstring)
    
    pubyear = row['pubyear']
    added_author_titles = row['added_author_titles']
    
    keywords2 = row['keywords2'] 
    keywords_form = row['keywords_form']
    
    #gar keine person angegeben
    if len(allauthorsdict) == 0:
      counternoauthor += 1
      continue
    
    #mehrere / keine mit Autorenrolle
    roles = [] 
    for author in allauthorsdict.values():
      roles.append(author['role'])
    
    if roles.count('aut') == 0:
      counternoauthor += 1
      continue
    
    if roles.count('aut') > 1:
      countermultipleauthors += 1
      continue
    
    #werksammlung
    leader7 = leader[7]
    field0086 = field008[6]
    
    if leader7=="b" or leader7=="c" or leader7=="s" or field0086=="c" or field0086=="d" or field0086=="i":
      countersammlung += 1
      continue
    
    if '-' in pubyear:
      countersammlungstrich += 1
      continue
    
    if '|' in added_author_titles:
      countersammlungaddedtitles += 1
      continue
    
    if 'DVD-ROM' in keywords2 or 'CD-ROM' in keywords2 :
      countersoftware += 1
      continue
    
    if (pubyear_erstauflage_008=="" or pubyear_erstauflage_008==9999 or pubyear_erstauflage_008=="9999") and pubyear=="":
      counternoyear += 1
      continue
    
    #preprocess those which are left
    #autorennamen
    for author, info in allauthorsdict.items():
      if info['role'] == 'aut':
        aut_authorname = author
        aut_author_gnd = info['author_gnd']
        aut_author_gnd_preprocessed = info['author_gnd_preprocessed']
        aut_author_lebensdaten = info['author_lebensdaten']
        aut_author_birth_year = info['author_birth_year']
        aut_author_death_year = info['author_death_year']
        
        #row['aut_authorname'] = aut_authorname
        row['aut_author_gnd'] = aut_author_gnd
        row['aut_author_gnd_preprocessed'] = aut_author_gnd_preprocessed
        row['aut_author_lebensdaten'] = aut_author_lebensdaten
        row['aut_author_birth_year'] = aut_author_birth_year
        row['aut_author_death_year'] = aut_author_death_year
        
        break
    
    if 'Hg' in aut_authorname or 'Hrsg' in aut_authorname or 'Herausgeber' in aut_authorname:
      counterhrsginauthor += 1
      continue
    
    if '&' in aut_authorname or 'u.a.' in aut_authorname:
      countermultipleauthors += 1
      continue
    
    aut_authorname = aut_authorname.strip()
    
    aut_authorname = re.sub(r"^,\s*", "", aut_authorname)
    aut_authorname = re.sub(r"^-\s*", "", aut_authorname)
    aut_authorname = re.sub(r"^-,\s*", "", aut_authorname)
    
    #weird whitespaces
    aut_authorname = re.sub(r'[\x00-\x1f]', '', aut_authorname)
    aut_authorname = re.sub(r"[\s\u00a0]+", " ", aut_authorname)
    
    aut_authorname = aut_authorname.replace(",,", ",")
    aut_authorname = aut_authorname.replace(" ,", ",")
    aut_authorname = aut_authorname.replace("Dr.", "")  
    aut_authorname = aut_authorname.replace("Prof.", "")  
    aut_authorname = aut_authorname.replace("Professor", "")  
    aut_authorname = aut_authorname.replace("(FH)", "")  
    aut_authorname = aut_authorname.replace("(Mag.)", "")  
    aut_authorname = aut_authorname.replace("-ing.", "")  
    aut_authorname = aut_authorname.replace("-Ing.", "")  
    aut_authorname = aut_authorname.replace("v.", "von")
    aut_authorname = aut_authorname.replace("(Bearbeiter), ","")
    aut_authorname = aut_authorname.replace("(SKG), ","")
    
    aut_authorname = aut_authorname.replace("  ", " ")
     
    #checked manually
    if 'bejot' in aut_authorname:
      row['aut_author_gnd'] = "112171206"
      row['aut_author_gnd_preprocessed'] = "112171206"
    
    if 'Ramses III' in aut_authorname:
      row['aut_author_gnd'] = "120290159X"
      row['aut_author_gnd_preprocessed'] = "120290159X"
    
    if '(geb. Jurow), Ludmila' in aut_authorname:
      row['aut_author_gnd'] = "1268388270"
      row['aut_author_gnd_preprocessed'] = "1268388270"
    
    if ', Christina Bartz' in aut_authorname:
      row['aut_author_gnd'] = "12176835X"  
      row['aut_author_gnd_preprocessed'] = "12176835X"
    
    if 'Feyerabend, Charly' in aut_authorname:
      aut_authorname = "Feyerabend, Charly von"    
    
    if 'Aarheyden, Konstantin' in aut_authorname:
      aut_authorname = "Aarheyden, Konstantin von"    
    
    if 'Abazi, H' in aut_authorname:
      aut_authorname = "Abazi, Hajdin"
      row['aut_author_gnd'] = "1143031016"
      row['aut_author_gnd_preprocessed'] = "1143031016"
    
    if 'Schachner' in aut_authorname and 'Marlene' in aut_authorname and 'Abdel' in aut_authorname:
      aut_authorname = "Abdel Aziz-Schachner, Marlene"
    
    if 'Abdel-Latif' in aut_authorname and 'Adel' in aut_authorname:
      aut_authorname = "Abdel-Latif, Adel"
      row['aut_author_gnd'] = "1077034539"
      row['aut_author_gnd_preprocessed'] = "1077034539"
    
    if 'Reitz-Dinse, Ann' in aut_authorname:
      row['aut_authorname'] = "Reitz-Dinse, Annegret"
      aut_authorname = "Reitz-Dinse, Annegret"
      row['aut_author_gnd'] = "120583496"      
      row['aut_author_gnd_preprocessed'] = "120583496"
    
    if any(name in aut_authorname for name in ['von Goehte, Johann Wolfgang', 'von Goethe, J. W.', 'Wolfgang von Goethe, Johann', 'Johann Wolfgang von, Goethe', 'von Goethe, Wolfgang', 'von Goethe, Johann-Wolfgang', 'Goethe, Johann W. von', 'Goethe, Johann Wolfang von']):
      aut_authorname = "von Goethe, Johann Wolfgang"
      row['aut_author_gnd'] = "118540238"    
      row['aut_author_gnd_preprocessed'] = "118540238"
    
    if '(Wiermann)' in aut_authorname:
      aut_authorname = "Wiermann, Jonamo"
    
    if '(Sarkar)' in aut_authorname:
      aut_authorname = "Chakraberty, Puja"    
    
    if 'Matting, Bußmann' in aut_authorname:
      aut_authorname = "Matting, Bußmann"   
    
    if 'Descartes, Re' in aut_authorname:
      aut_authorname = "Descartes, René"   
    
    if 'Klabund' in aut_authorname and 'Henschke' in aut_authorname:
      aut_authorname = "Alfred Georg Hermann Henschke, Klabund"
    
    if 's-Marie Arouet' in aut_authorname:
      aut_authorname = "François-Marie Arouet, Voltaire"
      row['aut_author_gnd'] = "118627813"    
      row['aut_author_gnd_preprocessed'] = "118627813"
    
    if '(Frantisek)' in aut_authorname:
      aut_authorname = "Kafka, František"
      row['aut_author_gnd'] = "1065770618"    
      row['aut_author_gnd_preprocessed'] = "1065770618"
    
    if '(Laozi)' in aut_authorname:
      aut_authorname = "Laozi"
      row['aut_author_gnd'] = "118569678"    
      row['aut_author_gnd_preprocessed'] = "118569678"    
    
    if 'Goetz, Christoph F.' in aut_authorname: 
      aut_authorname = "Goetz, Christoph F.-J."
      row['aut_author_gnd'] = "123122767"    
      row['aut_author_gnd_preprocessed'] = "123122767" 
    
    if 'Aristoteles von Stagira' in aut_authorname: 
      aut_authorname = "Aristoteles von Stagira"
      row['aut_author_gnd'] = "118650130"    
      row['aut_author_gnd_preprocessed'] = "118650130" 
    
    #fix gnd in names 
    gndpattern = r'^!(\d+X?)!$' 
    match = re.match(gndpattern, aut_authorname)
    if match:
      row['aut_author_gnd_preprocessed'] = match.group(1)
    
    if '1184409470' in aut_authorname:
      row['aut_author_gnd'] = "1184409470"    
      row['aut_author_gnd_preprocessed'] = "1184409470"
    
    if '124720796x' in aut_authorname:
      row['aut_author_gnd'] = "124720796X"    
      row['aut_author_gnd_preprocessed'] = "124720796X"
    
    #exception patterns
    # Hoffman, e,t,a.
    pattern1 = re.compile("[a-z],[a-z],[a-z],")
    if pattern1.search(aut_authorname):
      aut_authorname = re.sub(pattern1, lambda match: match.group().replace(",", "."), aut_authorname)
    
    #$P at beginning of name
    if '$P' in aut_authorname:
      aut_authorname = aut_authorname.replace("$P", "")
    
    
    aut_authorname_lebensdaten = re.sub('[^\d\- ]+', '', aut_authorname)
    if '-' in aut_authorname_lebensdaten:
      date_parts = aut_authorname_lebensdaten.strip().split("-") 
      authorname_birth_year = date_parts[0]
      authorname_death_year = date_parts[1]
      authorname_birth_year = authorname_birth_year.replace("X", "5")
      authorname_death_year = authorname_death_year.replace("X", "5")  
    else:
      authorname_birth_year, authorname_death_year = "", ""
    
    aut_authorname = re.sub(r'[0-9_()\*\[\]{}#~><\?!%$£$@&\^\\]+', '', aut_authorname)
    aut_authorname = re.sub(r'\s+', ' ', aut_authorname)
    author_named = aut_authorname
    
    if aut_authorname.count(",") == 1:
      lastname, firstname = aut_authorname.split(",")
      author_named = firstname.strip() + " " + lastname.strip()
    
    aut_authorname = aut_authorname.strip().lower()
    author_named = author_named.strip().lower()
    
    row['aut_authorname'] = aut_authorname
    row['author_named'] = author_named
    row['authorname_birth_year'] = authorname_birth_year
    row['authorname_death_year'] = authorname_death_year
    
    # Write the modified row to the output file
    writer.writerow(row)
    print(i)
    i+=1

print("countermultipleauthors:", countermultipleauthors)
print("counternoauthor:", counternoauthor)
print("countersammlung:", countersammlung)
print("countersammlungstrich:", countersammlungstrich)
print("countersammlungaddedtitles:", countersammlungaddedtitles)
print("countersoftware:", countersoftware)
print("counternoyear:", counternoyear)
print("counterhrsginauthor:", counterhrsginauthor)


#repeat with other parts
