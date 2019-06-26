import pandas
import json


error_indexes_array = []
max_error_counts = []
predicted_labels_array = []
words_array, true_label_array = [], []
files = ['baseline.txt', 'label_emb.txt', 'label_emb_mask.txt']
error_tags = ['__', '==', '--']

with open('./media_res/idx2w.json', 'r') as json_file:
    words_index = json.loads(json_file.read())  # 0 index.

for file_index, (origin_file, error_tag) in enumerate(zip(files, error_tags)):
    guessed_label_array = []
    error_indexes = []
    with open('./media_res/' + origin_file, 'r') as file:

        mini_w, mini_t, mini_g = [], [], []
        for line in file:
            if line is '\n':
                if file_index is 0:
                    words_array.append(mini_w)
                    true_label_array.append(mini_t)

                guessed_label_array.append(mini_g)
                mini_w, mini_t, mini_g = [], [], []
            else:
                line_array = line.split('&')
                if file_index is 0:
                    mini_w.append(words_index[str(int(line_array[0]) - 1)])
                    mini_t.append(line_array[1])

                mini_g.append(line_array[2][:-1])

    i = 0
    max_error_count = 0

    for sent_idx, (w_sentence, t_sentence, g_sentence) in enumerate(zip(words_array, true_label_array, guessed_label_array)):
        error_count = 0
        bError = False
        for index, (word, true_label, guess_label) in enumerate(zip(w_sentence, t_sentence, g_sentence)):
            if guess_label != true_label:
                if not bError:
                    i += 1
                    bError = True
                    error_indexes.append(sent_idx)
                error_count += 1
                w_sentence[index] = error_tag + word + error_tag
        if bError:
            max_error_count = error_count if error_count > max_error_count else max_error_count

    error_indexes_array.append(error_indexes)
    max_error_counts.append(max_error_count)
    predicted_labels_array.append(guessed_label_array)

print(max_error_counts)
intersection_errors = list(set(error_indexes_array[0]) | set(error_indexes_array[1]) | set(error_indexes_array[2]))
intersection_errors.sort()

print(len(intersection_errors))

for error_index in error_indexes_array[0]:
    print('--------------- SENTENCE nº {} --------------'.format(error_index))
    print(' '.join(words_array[error_index]))
    print(' | '.join(true_label_array[error_index]))
    print(' | '.join(predicted_labels_array[0][error_index]))
    print()
    print()


