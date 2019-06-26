import pandas as pd
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

data_df = pd.read_json('./json/correct-file.json', orient='index')

data_df['length'] = [len(tweet) for tweet in data_df['labels']]

print("The maximum length of a sentence is: " + str(max(data_df['length'])))
print("The minimum length of a sentence is: " + str(min(data_df['length'])))
print("The average length of a sentence is: " + str(sum(data_df['length'])/len(data_df['length'])))
print()

all_text_words = [item for sublist in data_df['text'] for item in sublist]
all_labels_words = [item[2:] if item is not 'O' else item for sublist in data_df['labels'] for item in sublist]

text_vocabulary = np.unique(all_text_words)
labels_vocabulary = np.unique(all_labels_words)

# text_vocabulary.append(word for word in all_text_words if word not in text_vocabulary)
# labels_vocabulary.append(word for word in all_labels_words if word not in labels_vocabulary)

train_word_counter = Counter(all_text_words)
most_common_words = train_word_counter.most_common(10)
dev_word_counter = Counter(all_labels_words)
most_common_labels = dev_word_counter.most_common(10)

print("The total number of words is: " + str(len(all_text_words)))
print("The length of the vocabulary is: " + str(len(text_vocabulary)))
print("Most common words:")
print(most_common_words)
print()
print("The total number of labels is: " + str(len(all_labels_words)))
print("The length of the labels vocabulary is: " + str(len(labels_vocabulary)))
print("Most common labels:")
print(most_common_labels)
print()

print(data_df.length.dtype)

data_df.plot(y='length', kind='hist')
plt.show()
