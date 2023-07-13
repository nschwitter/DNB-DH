import re
import pandas as pd
import numpy as np

authorinfo_titledata = pd.read_csv('converted/authorinfo_titledata_aftergndwikidata.csv')

authorinfo_titledata['birth_year_final'] = authorinfo_titledata['birth_year_final'].str.replace('X', '5')
authorinfo_titledata['birth_year_final'] = authorinfo_titledata['birth_year_final'].str.replace('x', '5')
authorinfo_titledata['birth_year_final'] = authorinfo_titledata['birth_year_final'].str.replace(r'\D', '')


titledata = pd.read_csv('converted/titeldaten_aftergnd.csv')
print(len(titledata))
titledata = titledata.drop(columns=['wd_birthyear', 'wd_deathyear'], errors='ignore')

tempidtofinalid = pd.read_csv('converted/tempidtofinalid.csv')

titledata2 = pd.merge(titledata, tempidtofinalid, on='aut_author_gnd_preprocessed', how="left")

titledata_id_info = pd.merge(titledata2, authorinfo_titledata, on="final_gnd_id", how="left")


def clean(row):
  auflage = row['auflage']
  auflage = str(auflage)
  
  auflage_cleaned = re.sub('[^\d]+', '', auflage)
  
  if auflage_cleaned == "" and ("Erst" in auflage or "Original" in auflage):
    auflage_cleaned = "1"
  
  if auflage_cleaned != "" and int(auflage_cleaned) > 1900:
    auflage_cleaned = ""
  
  row['auflage_cleaned'] = auflage_cleaned
  
  istneuauflage_cleaned = (bool(auflage_cleaned) and int(auflage_cleaned) > 1) or "Neuau" in auflage
  
  row['istneuauflage_cleaned'] = istneuauflage_cleaned
  
  pubyear = row['pubyear']
  pubyear_erstauflage = row['pubyear_erstauflage_008']
  pubyear_cleaned = pubyear_erstauflage
  
  if pubyear != "" and pubyear_erstauflage == "":
    pubyear_cleaned = re.sub('[^\d]+', '', pubyear)
  
  row['pubyear_cleaned'] = pubyear_cleaned
  
  return row

titledata_id_cleaned = titledata_id_info.apply(lambda row: clean(row), axis=1)

titledata_id_cleaned_pub = titledata_id_cleaned[(titledata_id_cleaned['pubyear_cleaned'].notna()) & (titledata_id_cleaned['pubyear_cleaned'].str.strip() != '') & (titledata_id_cleaned['pubyear_cleaned'] != 'nich') & (titledata_id_cleaned['pubyear_cleaned'] != '/1GB') & (titledata_id_cleaned['pubyear_cleaned'] != '/1IT') & (titledata_id_cleaned['pubyear_cleaned'] != '/1YU') & (titledata_id_cleaned['pubyear_cleaned'] != 'ohne')]

titledata_id_cleaned_pub['pubyear_cleaned'] = titledata_id_cleaned_pub['pubyear_cleaned'].str.replace('X', '5')
titledata_id_cleaned_pub['pubyear_cleaned'] = titledata_id_cleaned_pub['pubyear_cleaned'].str.replace('x', '5')
titledata_id_cleaned_pub['pubyear_cleaned'] = titledata_id_cleaned_pub['pubyear_cleaned'].str.replace('?', '5')
condition = titledata_id_cleaned_pub['pubyear_cleaned'].str.contains(r'\[202')
titledata_id_cleaned_pub.loc[condition, 'pubyear_cleaned'] = '2022'
condition = titledata_id_cleaned_pub['pubyear_cleaned'].str.contains(r'\[202') &  titledata_id_cleaned_pub['pubyear_neuauflage_008'].str.contains(r'1\]') 
titledata_id_cleaned_pub.loc[condition, 'pubyear_cleaned'] = '2021'
condition = titledata_id_cleaned_pub['pubyear_cleaned'].str.contains(r'\[198') 
titledata_id_cleaned_pub.loc[condition, 'pubyear_cleaned'] = '1987'
condition = titledata_id_cleaned_pub['pubyear_cleaned'].str.contains(r'\[201') 
titledata_id_cleaned_pub.loc[condition, 'pubyear_cleaned'] = '2017'
condition = titledata_id_cleaned_pub['pubyear_cleaned'].str.contains(r'\[182') 
titledata_id_cleaned_pub.loc[condition, 'pubyear_cleaned'] = '182'
condition = titledata_id_cleaned_pub['pubyear_cleaned'].str.contains(r'\[196') 
titledata_id_cleaned_pub.loc[condition, 'pubyear_cleaned'] = '1965'
condition = titledata_id_cleaned_pub['pubyear_cleaned'].str.contains(r'\[197') 
titledata_id_cleaned_pub.loc[condition, 'pubyear_cleaned'] = '1976'
condition = titledata_id_cleaned_pub['pubyear_cleaned'].str.contains(r'um 1') 
titledata_id_cleaned_pub.loc[condition, 'pubyear_cleaned'] = '1800'

print(len(titledata_id_cleaned_pub))


titledata_id_cleaned_pub['n_missing'] = titledata_id_cleaned_pub.isna().sum(axis=1)
titledata_id_cleaned_pub = titledata_id_cleaned_pub.sort_values(['final_gnd_id', 'pubyear_cleaned', 'titlesubtitle', 'n_missing'])

#dropping duplicates
mask = titledata_id_cleaned_pub.duplicated(subset=['final_gnd_id', 'pubyear_cleaned', 'titlesubtitle'], keep='first')
titledata_id_cleaned_nodupl = titledata_id_cleaned_pub[~mask]
print(len(titledata_id_cleaned_nodupl))

titledata_id_cleaned_nodupl = titledata_id_cleaned_nodupl.sort_values(['final_gnd_id', 'titlesubtitle', 'pubyear_cleaned'])
titledata_id_cleaned_nodupl['auflage_dataset'] = titledata_id_cleaned_nodupl.groupby(['titlesubtitle', 'final_gnd_id']).cumcount()

#drop if neuauflage, oder auflage groesser 1
titledata_id_cleaned_nodupl_singles = titledata_id_cleaned_nodupl[titledata_id_cleaned_nodupl['auflage_dataset'] == 0]
print(len(titledata_id_cleaned_nodupl_singles))

# Filter rows where istneuauflage_cleaned is True
mask = titledata_id_cleaned_nodupl_singles['istneuauflage_cleaned'] == True
rows_to_drop = titledata_id_cleaned_nodupl_singles[mask]

# Drop the filtered rows
titledata_id_cleaned_nodupl_singles = titledata_id_cleaned_nodupl_singles.drop(rows_to_drop.index)
print(len(titledata_id_cleaned_nodupl_singles))

# Drop all observations where birthyear is missing
titledata_id_cleaned_birth = titledata_id_cleaned_nodupl_singles.dropna(subset=['birth_year_final'])
titledata_id_cleaned_birth = titledata_id_cleaned_birth[(titledata_id_cleaned_birth['birth_year_final'].notna()) & (titledata_id_cleaned_birth['birth_year_final'].str.strip() != '') ]

print(len(titledata_id_cleaned_birth))

titledata_id_cleaned_birth.to_csv('converted/dataset_without_age.csv', index=False)

titledata_id_cleaned_birth['age'] = titledata_id_cleaned_birth['pubyear_cleaned'].astype(int) - titledata_id_cleaned_birth['birth_year_final'].astype(int) 


titledata_id_cleaned_birth_range = titledata_id_cleaned_birth[(titledata_id_cleaned_birth['age'] >= 18) & (titledata_id_cleaned_birth['age'] <= 79)]
print(len(titledata_id_cleaned_birth_range))


titledata_id_cleaned_birth_range.to_csv('converted/dataset_complete.csv', index=False)
