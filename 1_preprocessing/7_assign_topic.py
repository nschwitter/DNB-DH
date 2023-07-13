import nltk
import gensim

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer

import unicodedata
import re as re
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora, models
from gensim.models import CoherenceModel
from gensim.models import KeyedVectors
from sklearn.cluster import KMeans

from sklearn.metrics import silhouette_score



df = pd.read_csv("converted/dataset_complete_sentiment2.csv")

df = df[df['pubyear_cleaned'] >= 1913]


#drop irrelevant columns
df = df.drop(columns=['aut_author_gnd_preprocessed_x', 'id', 'leader', 'fixedlength008',
'isbn', 'other_ddc', 'lang_code', 'translated_lang_code', 'deutschsprachig', 
'laendercode', 'added_author_titles', 'added_titles', 'pubyear', 'pubyear_old', 'pubyear_erstauflage_008', 'pubyear_neuauflage_008', 'istneuauflage',
'auflage', 'aut_author_gnd_preprocessed_y', 'aut_authorname', 'author_named', 'aut_author_lebensdaten', 'aut_author_birth_year',
'aut_author_death_year', 'authorname_birth_year', 'authorname_death_year', 'author_lebensdaten', 'wd_personvalue', 'wd_mainname', 'wd_gnd',
'wd_names', 'isthesame', 'wd_birthyear_pre', 'wd_deathyear_pre', 'auflage_cleaned', 'istneuauflage_cleaned', 'n_missing', 'auflage_dataset'], axis=1)


def basicpreprocess(text):
  text = unicodedata.normalize('NFKD', text)
  text = ''.join(c for c in text if (unicodedata.category(c) in ['Ll', 'Lm', 'Lu', 'Mn']) or c in [' ', '-'])
  text = text.lower()
  return text

german_stopwords = set(stopwords.words("german"))
additional_stopwords = {"für", "the", "roman", "buch", "bücher", "-", "nan"}
stop_words = german_stopwords.union(additional_stopwords)

def advancedpreprocess(text):
  tokens = word_tokenize(text)
  tokens = [token for token in tokens if token not in stop_words and len(token)>3]
  #stemmer = SnowballStemmer("german")
  #stemmed_tokens = [stemmer.stem(token) for token in tokens]
  #stemmed_text = " ".join(stemmed_tokens)
  stemmed_text = " ".join(tokens) 
  return stemmed_text


sampling_percentage = 0.10  # 10% of the rows
num_rows_subsample = int(len(df) * sampling_percentage)
random_df = df.sample(n=num_rows_subsample, random_state=42)  # Set a random_state for reproducibility
random_df = random_df.reset_index(drop=True)

df = random_df

df['titlesubtitle_prepr'] = df['title_subtitle'].apply(basicpreprocess)
df['titlesubtitle_prepr_adv'] = df['titlesubtitle_prepr'].apply(advancedpreprocess)


###
# Method 1: Topic Modelling via Word Embeddings
###

word2vec = KeyedVectors.load_word2vec_format('wiki.de.vec', binary=False)

class WordVecVectorizer(object):
  def __init__(self, word2vec):
    self.word2vec = word2vec
    self.dim = 300    
  
  def fit(self, X, y):
    return self
  
  def transform(self, X):
    return np.array([
    np.mean([self.word2vec[w] for w in texts.split() if w in self.word2vec]
    or [np.zeros(self.dim)], axis=0)
    for texts in X
    ])
#representing each title by the mean of word embeddings for the words used 
wtv_vect = WordVecVectorizer(word2vec)
df_wtv = wtv_vect.transform(df.titlesubtitle_prepr)

print(df_wtv.shape)

#how many clusters fit best?
km = KMeans(n_clusters=8, init='random', n_init=10, max_iter=300, tol=1e-04, random_state=0)
#assign to dfs
y_km = km.fit_predict(df_wtv)

df.loc[:, 'topic_cluster_wordembed'] = y_km

df.to_csv("converted/df_sample_topics_wordembed.csv", index=False)


#ASSESS OPTIMAL NUMBER OF CLUSTERS
sse = []

# Try different values for the number of clusters (1 to 20)
for k in range(1, 40):
    km = KMeans(n_clusters=k, init='random', n_init=10, max_iter=300, tol=1e-04, random_state=0)
    km.fit(df_wtv)
    sse.append(km.inertia_)

# Plot the number of clusters vs. sum of squared distances
plt.plot(range(1, 40), sse, marker='o')
plt.xlabel('Number of clusters')
plt.ylabel('Sum of squared distances')
plt.title('Elbow Method')
plt.show()
plt.savefig('5_Results/figures/elbow_plot_sample.png')
plt.clf()


silhouette_scores = []

# Try different values for the number of clusters
for k in range(2, 40):
    km = KMeans(n_clusters=k, init='random', n_init=10, max_iter=300, tol=1e-04, random_state=0)
    labels = km.fit_predict(df_wtv)
    score = silhouette_score(df_wtv, labels)
    silhouette_scores.append(score)

# Plot the number of clusters vs. silhouette scores
plt.plot(range(2, 40), silhouette_scores, marker='o')
plt.xlabel('Number of clusters')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score')
plt.show()

plt.savefig('5_Results/figures/silhoutte_plot_sample.png')
plt.clf()


###
# Method 2: Clustering using LDA ( Latent Dirichlet Analysis)
###
# Preprocess the text
documents = df['titlesubtitle_prepr_adv'].tolist()

documents_tokenized = [word_tokenize(str(doc)) for doc in documents]

# Create a dictionary and corpus
dictionary = corpora.Dictionary(documents_tokenized)
corpus = [dictionary.doc2bow(doc) for doc in documents_tokenized]

# Perform LDA topic modeling
num_topics = 8  
lda_model = gensim.models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10)

#get words out
for topic_id in range(num_topics):
    words = lda_model.show_topic(topic_id, topn=20)
    topic_words = [word for word, _ in words]
    print(f"Topic {topic_id}: {topic_words}")

# Topic coherence
coherence_model = CoherenceModel(model=lda_model, texts=documents_tokenized, coherence='u_mass')
coherence_score = coherence_model.get_coherence()
print(f"Coherence Score: {coherence_score}")


# Iterate over different numbers of topics
for num_topics in range(1, 30):
    lda_model = gensim.models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10)

    # Get words for each topic
    for topic_id in range(num_topics):
        words = lda_model.show_topic(topic_id, topn=20)
        topic_words = [word for word, _ in words]
        print(f"Number of Topics: {num_topics}, Topic {topic_id}: {topic_words}")

    # Calculate coherence score
    coherence_model = CoherenceModel(model=lda_model, texts=documents_tokenized, coherence='u_mass')
    coherence_score = coherence_model.get_coherence()

    print(f"Number of Topics: {num_topics}, Coherence Score: {coherence_score}")
    print("-" * 40)

#coherence scores plotten
coherence_scores = [-5.5339082764986465, -6.208469789022121, -7.0399776860920555, -5.878580924306337, -7.014985010199427, -7.744309289633697, -7.8930397771127, -8.59567762851209, -9.317506075481104, -9.279429547855443, -9.84131217644479, -9.983689621117836, -10.9509610728632, -11.449886738358495, -11.35102956547227, -11.885245022055864, -12.064117011721686, -12.4853919914294, -12.631475406154811, -12.875251497657635, -13.149060511973351, -13.082956634100595, -13.656234215053214, -13.671864922764696, -13.866712856294773, -14.077675419399961, -14.295278084966624, -14.150683691889293, -14.490121810672845]

plt.plot(range(1, 30), coherence_scores, marker='o')
plt.xlabel('Number of clusters')
plt.ylabel('U-Mass Coherence Score')
plt.title('Coherence Score')
plt.show()

plt.savefig('5_Results/figures/coherence_plot_sample.png')
plt.clf()

topic_assignments = [lda_model.get_document_topics(doc) for doc in corpus]
df['topic_tpm'] = [max(topics, key=lambda x: x[1])[0] for topics in topic_assignments]

# Topic distribution analysis
topic_distribution = df['topic_tpm'].value_counts(normalize=True)
print("Topic Distribution:")
print(topic_distribution)

df.to_csv("converted/df_sample_topics_wordembed_tm.csv", index=False)

