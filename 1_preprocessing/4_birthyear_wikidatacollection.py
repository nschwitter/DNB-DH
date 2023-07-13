import requests
import json
import csv
import pandas as pd
import time
import os

###
## Fill in birth_year
###
authorinfo_titledata = pd.read_csv('converted/authorinfo_titledata_TOCHECKFORDUPLICATES.csv')

authorinfo_titledata['birth_year_final'] = authorinfo_titledata['aut_author_birth_year'].fillna(authorinfo_titledata['authorname_birth_year'])
authorinfo_titledata['death_year_final'] = authorinfo_titledata['aut_author_death_year'].fillna(authorinfo_titledata['authorname_death_year'])

print("Number of different authors in titledata: ", len(authorinfo_titledata))
print("Number of different authors with birthyear in titledata: ", len(authorinfo_titledata[authorinfo_titledata['birth_year_final'].notna()]))

authorinfo = pd.read_csv('converted/authorinfo.csv')

authorinfo_titledata = pd.merge(authorinfo_titledata, authorinfo, left_on='aut_author_gnd_preprocessed', right_on='id_gnd', how='left')

authorinfo_titledata['birth_year_final'] = authorinfo_titledata['birth_year'].fillna(authorinfo_titledata['authorname_birth_year'])
authorinfo_titledata['death_year_final'] = authorinfo_titledata['death_year'].fillna(authorinfo_titledata['authorname_death_year'])

authorinfo_titledata.drop(columns=['id_gnd', 'birth_year', 'death_year'], inplace=True)

print("Number of different authors with birthyear in titledata after GND: ", len(authorinfo_titledata[authorinfo_titledata['birth_year_final'].notna()]))


authorinfo_titledata.to_csv('converted/authorinfo_titledata_aftergnd.csv', index=False)

authorsinfo_titledata_without_birthyear = authorinfo_titledata.loc[authorinfo_titledata['birth_year_final'].isna(), ['aut_author_gnd_preprocessed', 'author_named']]
authorsinfo_titledata_without_birthyear = authorsinfo_titledata_without_birthyear.loc[~(authorsinfo_titledata_without_birthyear['aut_author_gnd_preprocessed'].str.startswith('NEW') & authorsinfo_titledata_without_birthyear.duplicated(subset=['author_named'], keep=False))]


url = "https://www.wikidata.org/w/api.php"
timeout = 7  # seconds
request_count = 0
MAX_REQUESTS = 200

def wikidatalookup(row):
  #timeouter
  global request_count
  if request_count >= MAX_REQUESTS:
    time.sleep(timeout)
    request_count = 0
  request_count += 1
  
  gnd_id = row['aut_author_gnd_preprocessed'] 
  person_name = row['author_named']
  if "NEW" not in gnd_id:
    params = {
      "action": "query",
      "format": "json",
      "list": "search",
      "srsearch": f"haswbstatement:P227={gnd_id}",
      "srnamespace": "0",
      "format": "json",
    }
    response = requests.get(url, params=params).json()
    if response['query']['searchinfo']['totalhits'] == 1:
      entity_id = response['query']['search'][0]['title'].replace('Item:', '')
    else:
      return pd.Series({'aut_author_gnd_preprocessed': gnd_id, 'author_named': person_name, 'wd_personvalue': float("NaN"), 'wd_mainname': float("NaN"), 'wd_birthyear': float("NaN"),  'wd_deathyear': float("NaN"), 'wd_gnd': float("NaN"),  'wd_names': float("NaN")}).to_frame().T
  elif pd.isna(person_name) or person_name=="":
    return pd.Series({'aut_author_gnd_preprocessed': gnd_id, 'author_named': person_name, 'wd_personvalue': float("NaN"), 'wd_mainname': float("NaN"), 'wd_birthyear': float("NaN"),  'wd_deathyear': float("NaN"), 'wd_gnd': float("NaN"),  'wd_names': float("NaN")}).to_frame().T
  else: 
    params = {
      "action": "wbsearchentities",
      "search": person_name,
      "language": "en",
      "format": "json",
    }
    response = requests.get(url, params=params).json()
    
    human_matches = []
    for result in response["search"]:
      entity_id = result["id"]
      entity_params = {
        "action": "wbgetentities",
        "ids": entity_id,
        "languages": "en",
        "format": "json",
        "props": "claims"
      }
      entity_response = requests.get(url, params=entity_params).json()
      if "claims" in entity_response.get("entities", {}).get(entity_id, {}):
        if "P31" in entity_response["entities"][entity_id]["claims"]:
          for claim in entity_response["entities"][entity_id]["claims"]["P31"]:
            if "mainsnak" in claim and "datavalue" in claim["mainsnak"]:
              if claim["mainsnak"]["datavalue"]["value"]["id"] == "Q5":
                human_matches.append(result)
                break
                      
    if len(human_matches) == 1:
      entity_id = human_matches[0]["id"]
    else:
      return pd.Series({'aut_author_gnd_preprocessed': gnd_id, 'author_named': person_name, 'wd_personvalue': float("NaN"), 'wd_mainname': float("NaN"), 'wd_birthyear': float("NaN"),  'wd_deathyear': float("NaN"), 'wd_gnd': float("NaN"),  'wd_names': float("NaN")}).to_frame().T
  
  params = {
    "action": "wbgetentities",
    "ids": entity_id,
    "languages": "de|en",
    "format": "json",
    "props": "labels|aliases|claims",
  }
  
  response = requests.get(url, params=params).json()
  
  try:
    label = response["entities"][entity_id]["labels"]["de"]["value"]
  except KeyError:
    # German label not found, try getting English label
    try:
        label = response["entities"][entity_id]["labels"]["en"]["value"]
    except KeyError:
        label = float("NaN")
        
  #label = response["entities"][entity_id]["labels"]["de"]["value"]
  claims = response["entities"][entity_id]["claims"]
  birth_year = claims.get("P569", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time", "")
  death_year = claims.get("P570", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time", "")
  claims = response["entities"][entity_id].get("claims", [])
  aliases = response["entities"][entity_id]["aliases"]
  values = [alias["value"] for lang_aliases in aliases.values() for alias in lang_aliases]
  gnd = claims.get("P227", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", "")
  
  return pd.Series({'aut_author_gnd_preprocessed': gnd_id, 'author_named': person_name, 'wd_personvalue': entity_id, 'wd_mainname': label, 'wd_birthyear': birth_year,  'wd_deathyear': death_year, 'wd_gnd': gnd,  'wd_names': values}).to_frame().T


def wikidatalookup_with_retry(row, max_retries=3, retry_wait=60):
  for i in range(max_retries):
    try:
      new_row = wikidatalookup(row)
      return new_row
    except KeyError:
      print("Key error encountered. Retrying in", retry_wait, "seconds...")
      time.sleep(retry_wait)
  print("Max retries exceeded. Returning None.")
  return None

authorsinfo_titledata_with_wikidata = pd.DataFrame(columns=['aut_author_gnd_preprocessed', 'author_named', 'wd_personvalue', 'wd_mainname', 'wd_birthyear', 'wd_deathyear', 'wd_gnd', 'wd_names'])
start_index = 0

for index, row in authorsinfo_titledata_without_birthyear.iloc[start_index:].iterrows():
  new_row = wikidatalookup_with_retry(row)
  if new_row is not None:
    new_row.to_csv('converted/authorinfo_from_wikidata.csv', mode='a', header=not os.path.exists('3_Daten/testdaten/authorinfo_from_wikidata.csv'), index=False)
    authorsinfo_titledata_with_wikidata = pd.concat([authorsinfo_titledata_with_wikidata, new_row]) # append the new DataFrame to the main DataFrame
  start_index = index + 1
  print("Index:", start_index)






##
# Check after
##
import csv
import pandas as pd
import numpy as np
import Levenshtein as lev
import ast
from unidecode import unidecode

authorinfo_titledata = pd.read_csv('converted/authorinfo_titledata_aftergnd.csv')


wikidata = pd.read_csv('converted/authorinfo_from_wikidata.csv')

print("Number of non-missing wikidata column:", wikidata['wd_personvalue'].notnull().sum())
print("Number of non-missing values in 'wd_birthyear' column:", wikidata['wd_birthyear'].notnull().sum())



def isthesameperson(gnd, str1, str2, alt_names):
  if "NEW" not in gnd:
    return True
  
  str1_lower = unidecode(str(str1)).lower()
  str2_lower = unidecode(str(str2)).lower()

  if str1_lower == str2_lower:
    return True
  
  if str1_lower.replace("-", " ") == str2_lower.replace("-", " "):
    return True
  
  alt_names_list = ast.literal_eval(alt_names)
  
  for alt_name in alt_names_list:
    alt_name_lower = unidecode(str(alt_name)).lower()
    if str1_lower == alt_name_lower:
      return True
    elif str1_lower.replace("-", " ") == alt_name_lower.replace("-", " "):
      return True
  
  lev_dist = lev.distance(str1_lower, str2_lower)
  rel_dist = lev_dist / max(len(str1_lower), len(str2_lower))
  if rel_dist >= 0.7:
    return True
  
  return False


wikidata_withoutmissing = wikidata.dropna(subset=['wd_birthyear'])
wikidata_withoutmissing = wikidata_withoutmissing.copy()
wikidata_withoutmissing.loc[:, 'isthesame'] = wikidata_withoutmissing.apply(lambda row: isthesameperson(row['aut_author_gnd_preprocessed'], row['author_named'], row['wd_mainname'], row['wd_names']), axis=1)

#additional manual checking
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "viktor toivo aaltonen", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "nils fritiof aberg", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "alexander aberle", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "ursula abramowski", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "ursula abramowski-lautenschläger", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "khalid abu-bakr", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "felix achilles", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "janis adamsons", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "sandor agoston", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "sabine ahrens", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "athanasius of alexandria", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "c. j. l. almquist", 'isthesame'] = True
wikidata_withoutmissing.loc[wikidata_withoutmissing['author_named'] == "hendrik w. j. van amerom", 'isthesame'] = True

wikidata_withoutmissing.to_csv('converted/wikidata_withoutmissing.csv', index=False)

#drop all those which are not the same person
wikidata_withoutmissing_filtered = wikidata_withoutmissing[wikidata_withoutmissing['isthesame'] == True]

authorinfo_titledata2 = pd.merge(authorinfo_titledata, wikidata_withoutmissing_filtered, on=['author_named', 'aut_author_gnd_preprocessed'], how="left")

authorinfo_titledata2.loc[:, 'final_gnd_id'] = authorinfo_titledata2['aut_author_gnd_preprocessed']
mask = authorinfo_titledata2['final_gnd_id'].str.contains('NEW', na=False)
authorinfo_titledata2.loc[mask & ~authorinfo_titledata2['wd_gnd'].isna(), 'final_gnd_id'] = authorinfo_titledata2['wd_gnd']


authorinfo_titledata2['wd_birthyear_pre'] = authorinfo_titledata2['wd_birthyear'].str.slice(1, 5)
authorinfo_titledata2['wd_deathyear_pre'] = authorinfo_titledata2['wd_deathyear'].str.slice(1, 5)

authorinfo_titledata2['birth_year_final'].fillna(authorinfo_titledata2['wd_birthyear_pre'], inplace=True)
authorinfo_titledata2['death_year_final'].fillna(authorinfo_titledata2['wd_deathyear_pre'], inplace=True)

#delete everything not needed
authorinfo_titledata2 = authorinfo_titledata2.drop(columns=['wd_birthyear', 'wd_deathyear'], errors='ignore')

authorinfo_titledata2 = pd.read_csv('3_Daten/gesamtabzug_titeldaten_konvertiert/authorinfo_titledata_aftergndwikidata.csv')


# Find duplicates and sort by birthyear
duplicates = authorinfo_titledata2[authorinfo_titledata2.duplicated(subset=['final_gnd_id'], keep=False)]
duplicates_sorted = duplicates.sort_values(['final_gnd_id', 'birth_year_final'])
# Drop duplicates and keep only earliest birthyear
earliest_birthyears = duplicates_sorted.drop_duplicates(subset=['final_gnd_id'], keep='first')

# Find non-duplicates
non_duplicates = authorinfo_titledata2[~authorinfo_titledata2['final_gnd_id'].duplicated(keep=False)]

# Concatenate the two DataFrames
authorinfo_titledata3 = pd.concat([earliest_birthyears, non_duplicates])

len(authorinfo_titledata3)

print("Number of different authors with birthyear in titledata after Wikidata: ", len(authorinfo_titledata3[authorinfo_titledata3['birth_year_final'].notna()]))
authorinfo_titledata3.to_csv('converted/authorinfo_titledata_aftergndwikidata.csv', index=False)

tempidtofinalid = authorinfo_titledata3[['final_gnd_id', 'aut_author_gnd_preprocessed']]
tempidtofinalid.to_csv('converted/tempidtofinalid.csv', index=False)
