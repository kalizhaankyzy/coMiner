import json
import math

import nltk
import numpy
import re
from utils.helpers import is_word, has_intersection, distance
from nltk.corpus import wordnet

DOCUMENTS_ROOT = './db/python/domain_mining/document_texts/'
DESCRIPTION_ROOT = './db/python/domain_mining/search_results/'
entity_name = 'Python'
competitors_list = ['R', 'Java', 'Javascript', 'Ruby', 'C', 'Js', 'Php', 'Go', 'Matlab']


def check_is_word_nltk(word_to_test):
    return wordnet.synsets(word_to_test)


def get_directory_of_document_text(name):
    return DOCUMENTS_ROOT + name + '_documentTexts.json'


def get_directory_of_descriptions(name):
    return DESCRIPTION_ROOT + name + '.json'


# get list of descriptions from one file
def extract_description_from_file(name):
    file_name_with_dir = get_directory_of_document_text(name)
    f = open(file_name_with_dir, encoding='utf-8')

    data = json.load(f)['descriptions']
    ans = []
    idx = 0
    for description in data:
        if description != '':
            ans.append(description)
        else:
            f_2 = open(get_directory_of_descriptions(name), encoding='utf-8')
            json_ = json.load(f_2)
            results = json_['results']
            result = results[idx]
            description_from_mother = result['description']
            ans.append(description_from_mother)
        idx += 1
    return ans


def phrase_from_one_description(description):
    arr = nltk.pos_tag(nltk.word_tokenize(description))
    ans = []
    for i in range(len(arr)-1):
        first_word_info = list(arr[i])
        second_word_info = list(arr[i+1])

        first_word, first_word_pos = first_word_info
        second_word, second_word_pos = second_word_info
        first_word = first_word.lower()
        second_word = second_word.lower()

        if is_word(first_word) and not has_intersection(first_word, competitors_list, entity_name) :
            if first_word_pos in ['NN', 'NNP', 'VP'] and len(first_word) > 3:
                if first_word_pos in ['NNS', 'NNPS','NNP','VBZ'] and len(first_word) > 3 and (first_word[-1]=='s'):
                    first_word = first_word[0:len(first_word) - 1]
                ans.append(first_word)
            if first_word_pos in ['VBG', 'JJ', 'NN', 'NNP', 'VP'] and second_word_pos in ['NN', 'NNP', 'VP', 'NNS','NNPS']:
                if is_word(second_word) and not has_intersection(second_word, competitors_list, entity_name):
                    if second_word_pos in ['NNS', 'NNPS','NNP','VBZ'] and (second_word[-1]=='s'):
                        second_word = second_word[0:len(second_word)-1]
                    ans.append((first_word+' '+second_word))

    return list(set(ans))


def phrase_from_descriptions_of_one_competitor(descriptions):
    print('Getting phrase from one competitor')
    return list(numpy.concatenate(list(map(phrase_from_one_description, descriptions))))


def get_all_phrases_from_list_of_description(descriptions_all):
    return list(set(list(numpy.concatenate(list(map(phrase_from_descriptions_of_one_competitor, descriptions_all))))))


def get_descriptions_list(descriptions_all):
    return list(numpy.concatenate(descriptions_all))


# Extracting files
c = extract_description_from_file('c')
php = extract_description_from_file('php')
java = extract_description_from_file('java')
javascript = extract_description_from_file('javascript')
js = extract_description_from_file('js')
go = extract_description_from_file('go')
r = extract_description_from_file('r')
matlab = extract_description_from_file('matlab')
ruby = extract_description_from_file('ruby')


descriptions_list_mapped = {
    'php': php,
    'javascript': javascript,
    'go': go,
    'r': r,
    'matlab': matlab,
    'ruby': ruby,
    'js': js,
    'c': c
}
lists_of_descriptions_of_each_competitor = list(descriptions_list_mapped.values())

list_of_phrases = get_all_phrases_from_list_of_description(lists_of_descriptions_of_each_competitor)
descriptions_list = get_descriptions_list(lists_of_descriptions_of_each_competitor)


def phrase_frequency(phrase, descriptions_list):
    text = ' '.join(descriptions_list)
    descriptions_word_array = nltk.word_tokenize(text.lower())
    return descriptions_word_array.count(phrase.lower())


def document_frequency(phrase, descriptions_list):
    cnt = 0
    for description in descriptions_list:
        description_word_array = nltk.word_tokenize(description.lower())
        if phrase.lower() in description_word_array:
            cnt += 1
    return cnt



def phrase_length(phrase):
    return len(phrase.lower().split(' '))


def average_distance(phrase, entity_name, descriptions_list_mapped):
    sum = 0
    n = 0
    for c_name in descriptions_list_mapped.keys():
        for description in descriptions_list_mapped.get(c_name):
            description = description.lower()
            phrase = phrase.lower()
            try:
                if re.search(r'\W' + phrase + r'\W', description) != None:
                    if ' ' in phrase:
                        p_new = phrase.replace(" ", '')
                        description = description.replace(phrase, p_new)
                        phrase = p_new

                    sum += (distance(description, entity_name, phrase) + distance(description, c_name, phrase))
                    n += 1
            except:
                return 45454

    if n == 0:
        return 12345

    return sum/(2*n)


# TODO implement this function
def cluster_entropy(phrase,descriptions_list):
    # arr = nltk.pos_tag(nltk.word_tokenize(description))
    C = []
    for desc in descriptions_list:
        if(phrase in desc):
            C.append(desc)


def phrase_independence(phrase, descriptions_list):
    appearment_list = []
    for description in descriptions_list:
        if(phrase in description):
            appearment_list.append(description)
    left_terms = set()
    right_terms = set()

    for description in appearment_list:
        description = description.lower()

        s = description.index(phrase)
        e = s + len(phrase)
        left_side = nltk.word_tokenize(description[0:s])
        right_side = nltk.word_tokenize(description[e:len(description)])

        for l in left_side:
            if(is_word(l)):
                left_terms.add(l)
        for r in right_side:
            if(is_word(r)):
                right_terms.add(r)
    PL, PR = 0, 0
    PF = len(appearment_list)
    left_terms = list(left_terms)
    right_terms = list(right_terms)
    for term in left_terms:
        F = len(re.findall(r'\b{}\b'.format(term), ' '.join(left_terms)))
        logga = 0
        if(PF !=0 and F!=0):
            logga = math.log2(F/ PF)
        PL += F/PF * logga
    for term in right_terms:
        F = len(re.findall(r'\b{}\b'.format(term), ' '.join(right_terms)))
        logga = 0
        if(PF !=0 and F!=0):
            logga = math.log2(F/ PF)
        PR += F/PF * logga
    return (PR+PF)/2


dica = {}
idx = 0
print(len(list_of_phrases))

for phrase in list_of_phrases:
    idx += 1
    print(idx, phrase)
    dica[phrase] = phrase_frequency(phrase, descriptions_list) * 0.138
    dica[phrase] += document_frequency(phrase, descriptions_list) * 0.06
    dica[phrase] += phrase_length(phrase) * 0.229
    dica[phrase] += average_distance(phrase, entity_name, descriptions_list_mapped) * (-0.073)
    dica[phrase] = phrase_independence(phrase, descriptions_list) * 0.187

ha = dict(sorted(dica.items(), key=lambda item: item[1], reverse=True))

print(list_of_phrases)
l = list(ha.keys())[0:30]
for i in l:
    print(i, ha[i])
print(ha['language'])