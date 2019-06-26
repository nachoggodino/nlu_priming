import pandas as pd
import numpy as np
from collections import Counter
import json

data_df = pd.read_csv('./csv/tree_df.csv', delimiter='\t', index_col=0)

data_df['tag'] = [tag if tag is 'O' else tag[2:] for tag in data_df['tag']]


word_vocabulary = np.unique(data_df.word)
label_vocabulary = np.unique(data_df.tag)

tree_dict = {}

data_df = data_df.sort_values(['tag', 'values']).reset_index(drop=True)
tags_words_df = data_df.groupby('tag')['word'].apply(np.array).reset_index(name='word')
word_counts_df = data_df.groupby('word').count().drop('values', axis=1).reset_index()
word_counts_df.columns = ['word', 'count']

for label in label_vocabulary:
    belonging_words = tags_words_df.loc[tags_words_df['tag'] == label, 'word'].values[0]
    counter = Counter(belonging_words)
    tree_dict[label] = {}
    for word in counter.most_common():
        tree_dict[label][word[0]] = float(word[1])/float(word_counts_df.loc[word_counts_df['word'] == word[0], 'count'].values[0])

print(tree_dict)
print(json.dumps(tree_dict))

with open('./json/tree_output.json', 'w', encoding='utf-8') as outfile:
    json.dump(tree_dict, outfile, ensure_ascii=False, indent=4)

