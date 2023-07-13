import csv
import pandas as pd


###
## preprocess titledata
###
print("start titeldata preprocessing")
results = pd.read_csv('converted/titeldaten_complete.csv')
nametoid_titledata = pd.read_csv('converted/nametoid_titledata.csv')

counts = nametoid_titledata.groupby('aut_authorname').size().reset_index(name='count')
nametoid_titledata_once = counts[counts['count'] == 1]['aut_authorname']

#create authorstitledata with unique IDs; missing data will be filled in by titledata, gnd and wikidata

#find those without ID and fill them up
authors_without_gnd = results[['aut_authorname', 'aut_author_gnd_preprocessed']]
authors_without_gnd = authors_without_gnd[authors_without_gnd['aut_author_gnd_preprocessed'].isna()]
authors_without_gnd = authors_without_gnd.drop_duplicates()

#gnd-id auffuellen von titeldaten -> nur, wenn eindeutig
authors_without_gnd_temp = authors_without_gnd.drop(columns=['aut_author_gnd_preprocessed'])
authors_without_gnd2 = pd.merge(authors_without_gnd_temp, nametoid_titledata[nametoid_titledata['aut_authorname'].isin(nametoid_titledata_once)], on='aut_authorname',  how='left')
authors_without_gnd2 = authors_without_gnd2[authors_without_gnd2['aut_author_gnd_preprocessed'].notna()]

#merge back 
if len(authors_without_gnd2)>0:
  results = pd.merge(results, authors_without_gnd2, on='aut_authorname', how='left')
  results = results.rename(columns={'aut_author_gnd_preprocessed_x': 'aut_author_gnd_preprocessed'})
  results['aut_author_gnd_preprocessed'].fillna(results['aut_author_gnd_preprocessed_y'], inplace=True)
  results.drop(columns=['aut_author_gnd_preprocessed_y'], inplace=True)


#gnd-id auffuellen von titeldaten 2 -> nur, wenn eindeutig
authors_without_gnd = results[['aut_author_gnd_preprocessed', 'author_named']]
authors_without_gnd = authors_without_gnd[authors_without_gnd['aut_author_gnd_preprocessed'].isna()]
authors_without_gnd = authors_without_gnd.drop_duplicates()

authors_without_gnd_temp = authors_without_gnd.drop(columns=['aut_author_gnd_preprocessed'])

authors_without_gnd3 = pd.merge(authors_without_gnd_temp, nametoid_titledata[nametoid_titledata['aut_authorname'].isin(nametoid_titledata_once)], left_on='author_named', right_on='aut_authorname',  how='left')
authors_without_gnd3 = authors_without_gnd3.drop(labels=['aut_authorname'], axis=1)
authors_without_gnd3 = authors_without_gnd3[authors_without_gnd3['aut_author_gnd_preprocessed'].notna()]

#merge back
if len(authors_without_gnd3)>0:
  results = pd.merge(results, authors_without_gnd3, on='author_named', how='left')
  results = results.rename(columns={'aut_author_gnd_preprocessed_x': 'aut_author_gnd_preprocessed'})
  results['aut_author_gnd_preprocessed'].fillna(results['aut_author_gnd_preprocessed_y'], inplace=True)
  results.drop(columns=['aut_author_gnd_preprocessed_y'], inplace=True)


#gnd-id auffuellen von namestoid -> nur, wenn eindeutig
print("start merging with gnd")

nametoid = pd.read_csv('converted/nametoid.csv')

counts = nametoid.groupby('listofnames').size().reset_index(name='count')
nametoid_once = counts[counts['count'] == 1]['listofnames']

authors_without_gnd = results[['aut_authorname', 'aut_author_gnd_preprocessed']]
authors_without_gnd = authors_without_gnd[authors_without_gnd['aut_author_gnd_preprocessed'].isna()]
authors_without_gnd = authors_without_gnd.drop_duplicates()

authors_without_gnd_temp = authors_without_gnd.drop(columns=['aut_author_gnd_preprocessed'])

authors_without_gnd4 = pd.merge(authors_without_gnd_temp, nametoid[nametoid['listofnames'].isin(nametoid_once)], left_on='aut_authorname', right_on='listofnames', how='left')
authors_without_gnd4.drop(columns=['listofnames'], inplace=True)
authors_without_gnd4 = authors_without_gnd4[authors_without_gnd4['id_gnd'].notna()]

#merge back
if len(authors_without_gnd4)>0:
  results = pd.merge(results, authors_without_gnd4, on='aut_authorname', how='left')
  results['aut_author_gnd_preprocessed'].fillna(results['id_gnd'], inplace=True)
  results.drop(columns=['id_gnd'], inplace=True)


#gnd-id auffuellen von namestoid 2 -> nur, wenn eindeutig
authors_without_gnd = results[['author_named', 'aut_author_gnd_preprocessed']]
authors_without_gnd = authors_without_gnd[authors_without_gnd['aut_author_gnd_preprocessed'].isna()]
authors_without_gnd = authors_without_gnd.drop_duplicates()

authors_without_gnd_temp = authors_without_gnd.drop(columns=['aut_author_gnd_preprocessed'])

authors_without_gnd5 = pd.merge(authors_without_gnd_temp, nametoid[nametoid['listofnames'].isin(nametoid_once)], left_on='author_named', right_on='listofnames', how='left')
authors_without_gnd5.drop(columns=['listofnames'], inplace=True)
authors_without_gnd5 = authors_without_gnd5[authors_without_gnd5['id_gnd'].notna()]

#merge back
if len(authors_without_gnd5)>0:
  results = pd.merge(results, authors_without_gnd5, on='author_named', how='left')
  results['aut_author_gnd_preprocessed'].fillna(results['id_gnd'], inplace=True)
  results.drop(columns=['id_gnd'], inplace=True)



###
## Create dataframes
###

print("done merging with gnd, create new ids")

titledata_aftergnd = results.sort_values('aut_authorname').reset_index(drop=True)

titledata_aftergnd['name_group'] = titledata_aftergnd.groupby('aut_authorname').ngroup()

# create a dictionary of existing gnd_id values
existing_ids = titledata_aftergnd.dropna(subset=['aut_author_gnd_preprocessed']) \
                                         .groupby('name_group')['aut_author_gnd_preprocessed'] \
                                         .unique().to_dict()
                                         

# create a dictionary of new ids for groups without an existing id
new_ids = {group_id: 'NEW' + str(i+1) for i, group_id in enumerate(titledata_aftergnd['name_group'].unique()) \
                                     if group_id not in existing_ids}

# fill in missing gnd_id values
titledata_aftergnd['aut_author_gnd_preprocessed'] = \
    titledata_aftergnd.groupby(['name_group'])['aut_author_gnd_preprocessed'] \
                               .apply(lambda x: x.fillna(new_ids[x.name]) if x.name in new_ids else x)

# remove temporary column
titledata_aftergnd = titledata_aftergnd.drop(columns=['name_group'])


nan_indices = titledata_aftergnd['aut_author_gnd_preprocessed'].isnull()
titledata_aftergnd.loc[nan_indices, 'aut_author_gnd_preprocessed'] = ["NEW" + str(i) for i in range(100000000, 100000000 + nan_indices.sum())]


titledata = titledata_aftergnd[['aut_author_gnd_preprocessed', 'id', 'leader', 'fixedlength008', 'isbn', 'ddc', 'other_ddc','belletristik', 'lang_code', 'translated_lang_code', 'deutschsprachig','uebersetzung', 'laendercode', 'added_author_titles', 'added_titles', 'title','subtitle', 'titlesubtitle', 'pubyear', 'pubyear_old', 'pubyear_erstauflage_008', 'pubyear_neuauflage_008', 'istneuauflage', 'auflage', 'keywords', 'keywords2', 'zeitschlagwort', 'geografika', 'keywords_form', 'nebeneintragung']]
titledata.to_csv('converted/titeldaten_aftergnd.csv', index=False)


nametoid_titledata_aftergnd = titledata_aftergnd[['aut_author_gnd_preprocessed', 'aut_authorname', 'author_named']]
nametoid_titledata_aftergnd = nametoid_titledata_aftergnd.drop_duplicates()


nametoid_titledata_aftergnd_temp = nametoid_titledata_aftergnd[['aut_author_gnd_preprocessed', 'author_named']].rename(columns={'author_named': 'aut_authorname'})
nametoid_titledata_aftergnd = pd.concat([nametoid_titledata_aftergnd[['aut_author_gnd_preprocessed', 'aut_authorname']], nametoid_titledata_aftergnd_temp])

nametoid_titledata_aftergnd.to_csv('converted/nametoid_titeldaten_aftergnd.csv', index=False)

authorinfo = titledata_aftergnd.loc[:, ['aut_author_gnd_preprocessed', 'aut_authorname', 'author_named', 'aut_author_lebensdaten', 'aut_author_birth_year', 'aut_author_death_year', 'authorname_birth_year', 'authorname_death_year']].copy()
authorinfo = authorinfo.drop_duplicates()

#when there are two with same id, i keep the one with lebensdaten
authorinfo_sorted = authorinfo.sort_values(['aut_author_gnd_preprocessed', 'aut_author_lebensdaten'])

authorinfo_noduplicates = authorinfo_sorted.drop_duplicates(subset=['aut_author_gnd_preprocessed'], keep='last')
authorinfo_noduplicates = authorinfo_noduplicates.copy()
authorinfo_noduplicates.drop_duplicates(inplace=True) 

authorinfo_noduplicates = authorinfo_noduplicates.sort_values('aut_authorname')
authorinfo_noduplicates.to_csv('converted/authorinfo_titledata_TOCHECKFORDUPLICATES.csv', index=False)

#todo here: manual checking
