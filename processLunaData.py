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
    directories = ['JAKDOJECHAC', 'KIEDY', 'ZNIZKI']
    f_m = ['F', 'M']
    for directory in directories:
        for folder in f_m:
            for name in os.listdir('./dataset/{}/{}/'.format(directory, folder)):
                data_path = './dataset/{}/{}/{}/'.format(directory, folder, name)
                print('----------------- Processing {} ------------------'.format(data_path))
                data_code = name[:6]
                words_file = data_code + 'words.xml'
                turns_file = data_code + 'turns.xml'
                chunks_file = data_code + 'chunks.xml'

                words_df = xml_to_df(data_path + words_file)
                turns_df = xml_to_df(data_path + turns_file)
                chunks_df = xml_to_df(data_path + chunks_file)

                turns_df['words'] = [[subwords.split('_')[-1] for subwords in word.split('..')] for word in turns_df['words']]
                chunks_df['span'] = [[subwords.split('_')[-1] for subwords in word.split('..')] for word in chunks_df['span']]

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

                chunks_for_words_array = []
                BIO_tags_array = []
                next_chunk = 1
                for index in range(1, len(words_df.index) + 1):
                    gotcha = False
                    for chunk in chunks_df.index:
                        if gotcha:
                            continue
                        start = int(chunks_df['span'][chunk][0])
                        if len(chunks_df['span'][chunk]) < 2:
                            end = int(chunks_df['span'][chunk][0]) + 1
                        else:
                            end = int(chunks_df['span'][chunk][1]) + 1

                        my_range = range(start, end)

                        if index in my_range:
                            chunks_for_words_array.append(chunk + 1)
                            if chunk + 1 == next_chunk:
                                BIO_tags_array.append('B-' + chunks_df['cat'][next_chunk - 1])
                                next_chunk += 1
                            else:
                                BIO_tags_array.append('I-' + chunks_df['cat'][next_chunk - 2])
                            gotcha = True

                words_df['chunk'] = chunks_for_words_array
                words_df['BIO_tag'] = BIO_tags_array

                words_in_turns_array = []
                tags_in_turns_array = []
                for turn in turns_df.index + 1:
                    words_in_turns_array.append(words_df.loc[words_df['turn'] == turn, 'word'].values)
                    tags_in_turns_array.append(words_df.loc[words_df['turn'] == turn, 'BIO_tag'].values)

                turns_df['word_array'] = words_in_turns_array
                turns_df['tags_array'] = tags_in_turns_array

                print(turns_df['tags_array'])
                print(turns_df['word_array'])

# Han hecho falta las siguientes ediciones de los datos, por erratas:
#     - JAKDOJECHAC/F/00961: La última palabra se ha quitado por no estar tenida en cuenta en los demás ficheros.
#     - ZNIZKI/F/20057: Las palabras 48 a 50 se han agrupado puesto que no aparecían la 49 y 50 en chunks.
#     - ZNIZKI/F/20057: Las palabras 52 a 55 se han agrupado puesto que no aparecían la 53, 54 y 55 en chunks.
#     - ZNIZKI/F/00693: Las palabras 116 a 119 se han agrupado puesto que no aparecían la 117, 118 y 119 en chunks.




