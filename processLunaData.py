import xml.etree.ElementTree as ET
import pandas as pd
import os


def xml_to_df(path):
    tree = ET.parse(path)
    root = tree.getroot()
    array = []
    for element in root:
        array.append(element.attrib)
    return pd.DataFrame.from_dict(array, orient='columns')


if __name__ == '__main__':
    base_directory = "./dataset/LUNA.PL/LUNA.PL"
    directories = ['CZYJEDZIEPRZEZ', 'JAKDOJECHAC', 'KIEDY', 'PRZYSTANKI', 'ZNIZKI']
    dobra_kieps = ['DOBRAJAKOSC', 'KIEPSKAJAKOSC']
    f_m = ['F', 'M']
    resulting_array = []
    tree_resulting_array = []
    for directory in directories:
        print('Exploring {}...'.format(directory))
        for folder in dobra_kieps:
            print('    Subdirectory {}...'.format(folder))
            for subfolder in f_m:
                print('        Subdirectory {}...'.format(subfolder))
                for name in os.listdir('{}/{}/{}/{}'.format(base_directory, directory, folder, subfolder)):
                    data_path = '{}/{}/{}/{}/{}/'.format(base_directory, directory, folder, subfolder, name)
                    data_code = name
                    print('            Folder with code {}'.format(data_code))
                    words_file = data_code + '_words.xml'
                    turns_file = data_code + '_turns.xml'
                    chunks_file = data_code + '_chunks.xml'
                    att_file = data_code + '_attvalue.xml'

                    words_df = xml_to_df(data_path + words_file)
                    turns_df = xml_to_df(data_path + turns_file)
                    chunks_df = xml_to_df(data_path + chunks_file)
                    att_df = xml_to_df(data_path + att_file)

                    turns_df['words'] = [[subwords.split('_')[-1] for subwords in word.split('..')] for word in turns_df['words']]
                    chunks_df['span'] = [[subwords.split('_')[-1] for subwords in word.split('..')] for word in chunks_df['span']]
                    att_df['span'] = [[subwords.split('_')[-1] for subwords in word.split('..')] for word in att_df['span']]

                    # Phase 1. Add to the words DF a field with the turn they belong to.
                    turns_for_words_array = []
                    for index in range(0, len(words_df.index) + 1):
                        gotcha = False
                        for turn in turns_df.index:
                            if (turns_df['words'][turn][0] == 'empty') or gotcha:
                                continue

                            start = int(turns_df['words'][turn][0])
                            if len(turns_df['words'][turn]) < 2:
                                end = int(turns_df['words'][turn][0]) + 1
                            else:
                                end = int(turns_df['words'][turn][1]) + 1

                            my_range = range(start, end)

                            if index in my_range:
                                turns_for_words_array.append(turn + 1)
                                gotcha = True

                    words_df['turn'] = turns_for_words_array

                    # Phase 2. Add to the words DF two fields, the chunk (or attribute) they belong to and its BIO tag.
                    chunks_for_words_array = []
                    BIO_tags_array = []
                    values_for_words_array = []
                    next_chunk = 1
                    tag = 'attribute'  # Tag for BIO tags.

                    for index in range(1, len(words_df.index) + 1):
                        gotcha = False
                        for chunk in att_df.index:
                            if gotcha:
                                continue
                            start = int(att_df['span'][chunk][0])
                            if len(att_df['span'][chunk]) < 2:
                                end = int(att_df['span'][chunk][0]) + 1
                            else:
                                end = int(att_df['span'][chunk][1]) + 1

                            my_range = range(start, end)

                            if index in my_range:
                                chunks_for_words_array.append(chunk + 1)
                                values_for_words_array.append(att_df['value'][chunk])
                                if chunk + 1 == next_chunk:
                                    BIO_tags_array.append('B-' + att_df[tag][next_chunk - 1])
                                    next_chunk += 1
                                else:
                                    BIO_tags_array.append('I-' + att_df[tag][next_chunk - 2])
                                gotcha = True
                        if not gotcha:
                            BIO_tags_array.append('O')
                            chunks_for_words_array.append(0)
                            values_for_words_array.append('O')

                    words_df['chunk'] = chunks_for_words_array
                    words_df['BIO_tag'] = BIO_tags_array
                    words_df['value'] = values_for_words_array

                    tree_resulting_array.append(pd.DataFrame({'word': words_df['word'], 'tag': BIO_tags_array, 'values': values_for_words_array}))

                    # Phase 3. Add two fields to the turns DF, array of belonging words and array of related tags.
                    words_in_turns_array = []
                    tags_in_turns_array = []
                    for turn in turns_df.index + 1:
                        if words_df.loc[words_df['turn'] == turn, 'word'].values.size == 0:
                            print("                Empty array removed!")
                            continue
                        words_in_turns_array.append(words_df.loc[words_df['turn'] == turn, 'word'].values)
                        tags_in_turns_array.append(words_df.loc[words_df['turn'] == turn, 'BIO_tag'].values)

                    # Phase 4. Create an array and append the sentences, containing array of words and array of tags.
                    resulting_array.append(pd.DataFrame({'text': words_in_turns_array, 'labels': tags_in_turns_array}))
                    for index, array in enumerate(tags_in_turns_array):
                        if array[0][0] is 'I':
                            print("                Turning {} into {}".format(tags_in_turns_array[index][0], 'B' + tags_in_turns_array[index][0][1:]))
                            tags_in_turns_array[index][0] = 'B' + tags_in_turns_array[index][0][1:]

    resulting_df = pd.concat(resulting_array, ignore_index=True)
    tree_resulting_df = pd.concat(tree_resulting_array, ignore_index=True)

    with open('./csv/tree_df.csv', 'w', encoding='utf-8') as file:
        tree_resulting_df.to_csv(file, sep='\t', encoding='utf-8')

    with open('./json/output.json', 'w', encoding='utf-8') as file:
        resulting_df.to_json(file, orient='index', force_ascii=False)
