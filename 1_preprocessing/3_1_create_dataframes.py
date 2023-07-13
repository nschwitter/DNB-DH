import csv
import pandas as pd

###
## GND
###
gndfilename = 'converted/dnbmarc-gnd-person_20221013.csv'
gnddf = pd.read_csv(gndfilename)

nametoid = gnddf.loc[:, ['id_gnd', 'author', 'author_furthernames']].copy()

nametoid['listofnames'] = nametoid['author'].str.lower() + '|' + nametoid['author_furthernames'].str.lower()

nametoid = nametoid.drop(['author', 'author_furthernames'], axis=1)

nametoid = nametoid.assign(listofnames=nametoid['listofnames'].str.split('|')).explode('listofnames')
nametoid.head()


# Define function to swap first and last names
def swap_names(name):
  if pd.isna(name):
    return name
  if "," in name:
    name_parts = name.split(",")
    if len(name_parts) != 2:
      return name
    lastname, firstname = name_parts
    author_named = firstname.strip() + " " + lastname.strip()
    return author_named  
  else:
    return name

# Apply function to create new column
nametoid['listofnames2'] = nametoid['listofnames'].apply(swap_names)

nametoid.head()

nametoid_temp = nametoid[['id_gnd', 'listofnames2']].rename(columns={'listofnames2': 'listofnames'})
nametoid = pd.concat([nametoid[['id_gnd', 'listofnames']], nametoid_temp], ignore_index=True)

nametoid = nametoid.drop_duplicates()

nametoid.sort_values(['id_gnd', 'listofnames'], inplace=True)
nametoid.reset_index(drop=True, inplace=True)

nametoid.head()

#nametoid -> all gnd names
nametoid.to_csv('converted/nametoid.csv', index=False)


#authorinfo from gnd
authorinfo = gnddf.loc[:, ['id_gnd', 'author_lebensdaten', 'birth_year', 'death_year']].copy()

authorinfo = authorinfo.drop_duplicates()

authorinfo.to_csv('converted/authorinfo.csv', index=False)


###
## Concat titledatata
###

filename1 = 'converted/dnb_all_dnbmarc_20221013-1_filtered.csv'
filename2 = 'converted/dnb_all_dnbmarc_20221013-2_filtered.csv'
filename3 = 'converted/dnb_all_dnbmarc_20221013-3_filtered.csv'
filename4 = 'converted/dnb_all_dnbmarc_20221013-4_filtered.csv'
filename5 = 'converted/dnb_all_dnbmarc_20221013-5_filtered.csv'

df1 = pd.read_csv(filename1)
df2 = pd.read_csv(filename2)
df3 = pd.read_csv(filename3)
df4 = pd.read_csv(filename4)
df5 = pd.read_csv(filename5)

results = pd.concat([df1, df2, df3, df4, df5])

results.to_csv('converted/titeldaten_complete.csv', index=False)


###
## Titledata: get ID
###

results = pd.read_csv('converted/titeldaten_complete.csv')

nametoid_titledata = results[['aut_authorname', 'aut_author_gnd_preprocessed', 'author_named']]

nametoid_temp = nametoid_titledata[['aut_author_gnd_preprocessed', 'author_named']].rename(columns={'author_named': 'aut_authorname'})

nametoid_titledata = pd.concat([nametoid_titledata[['aut_author_gnd_preprocessed', 'aut_authorname']], nametoid_temp], ignore_index=True)

nametoid_titledata = nametoid_titledata.drop_duplicates()

nametoid_titledata.sort_values(['aut_author_gnd_preprocessed', 'aut_authorname'], inplace=True)
nametoid_titledata.reset_index(drop=True, inplace=True)

#nametoid_titledata.head()

nametoid_titledata.dropna(inplace=True)

nametoid_titledata.to_csv('converted/nametoid_titledata.csv', index=False)
