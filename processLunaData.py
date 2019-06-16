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
    resulting_array = []
    for directory in directories:
        print('Exploring {}...'.format(directory))
        for folder in f_m:
            print('    Subdirectory {}...'.format(folder))
            for name in os.listdir('./dataset/{}/{}/'.format(directory, folder)):
                data_path = './dataset/{}/{}/{}/'.format(directory, folder, name)
                data_code = name[:6]
                print('        Folder with code {}'.format(data_code[:5]))
                words_file = data_code + 'words.xml'
                turns_file = data_code + 'turns.xml'
                chunks_file = data_code + 'chunks.xml'
                att_file = data_code + 'attvalue.xml'

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
                            if chunk + 1 == next_chunk:
                                BIO_tags_array.append('B-' + att_df[tag][next_chunk - 1])
                                next_chunk += 1
                            else:
                                BIO_tags_array.append('I-' + att_df[tag][next_chunk - 2])
                            gotcha = True
                    if not gotcha:
                        BIO_tags_array.append('O')
                        chunks_for_words_array.append(0)

                words_df['chunk'] = chunks_for_words_array
                words_df['BIO_tag'] = BIO_tags_array

                # Phase 3. Add two fields to the turns DF, array of belonging words and array of related tags.
                words_in_turns_array = []
                tags_in_turns_array = []
                for turn in turns_df.index + 1:
                    words_in_turns_array.append(words_df.loc[words_df['turn'] == turn, 'word'].values)
                    tags_in_turns_array.append(words_df.loc[words_df['turn'] == turn, 'BIO_tag'].values)

                turns_df['word_array'] = words_in_turns_array
                turns_df['tags_array'] = tags_in_turns_array

                # Phase 4. Create an array and append the sentences, containing array of words and array of tags.
                resulting_array.append(pd.DataFrame({'text': words_in_turns_array, 'labels': tags_in_turns_array}))

    resulting_df = pd.concat(resulting_array, ignore_index=True)
    with open('./output.json', 'w', encoding='utf-8') as file:
        resulting_df.to_json(file, orient='index', force_ascii=False)

# Han hecho falta las siguientes ediciones de los datos, por erratas, en los archivos chunks.xml:
#     - JAKDOJECHAC/F/00961: La última palabra se ha quitado por no estar tenida en cuenta en los demás ficheros.
#     - ZNIZKI/F/20057: Las palabras 48 a 50 se han agrupado puesto que no aparecían la 49 y 50 en chunks.
#     - ZNIZKI/F/20057: Las palabras 52 a 55 se han agrupado.
#     - ZNIZKI/F/00693: Las palabras 116 a 119 se han agrupado.
#     - ZNIZKI/F/00962: Las palabras 194 a 197 se han agrupado.
#     - ZNIZKI/F/00962: Las palabras 146 a 149 se han agrupado.
#     - ZNIZKI/F/00200: Las palabras 157 a 159 se han agrupado.
#     - ZNIZKI/F/00024: Las palabras 159 a 162 se han agrupado.
#     - ZNIZKI/F/20075: Las palabras 98 a 101 se han agrupado.
#     - ZNIZKI/F/00021: Las palabras 265 a 268 y 134 a 137 se han agrupado.
#     - ZNIZKI/F/00105: Las palabras 93 a 95 y 121 a 123 se han agrupado.
#     - ZNIZKI/M/00761: Las palabras 129 a 132 se han agrupado.
#     - ZNIZKI/M/10003: Las palabras 88 a 91 se han agrupado.
#     - ZNIZKI/M/10014: Las palabras 70 a 72 se han agrupado.
#     - ZNIZKI/M/20037: Las palabras 59 a 62 se han agrupado.
#     - ZNIZKI/M/10023: Las palabras 130 a 133, 126 a 128 y 69 a 72 se han agrupado.
#     - ZNIZKI/M/20021: Las palabras 50 a 52, 54 a 57, 110 a 113 y 106 a 108 se han agrupado.
#     - ZNIZKI/M/10000: Las palabras 54 a 56 se han agrupado.




