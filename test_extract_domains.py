import json
import math
import nltk
import numpy
import re
from utils.helpers import is_word, has_intersection, distance
from nltk.corpus import wordnet

from nltk.corpus import stopwords
stop_words = stopwords.words('english')


def filterize(arr):
    ans = []
    for word in arr:
        if word.lower() not in stop_words:
            ans.append(word)
    return ans

# check if a string is word using nltk
def check_is_word_nltk(word_to_test):
    return wordnet.synsets(word_to_test)


# get directory to documents file by competitor name
def get_directory_of_document_text(name, entity_name):
    return './db/{}/domain_mining/document_texts/'.format(entity_name) + name + '_documentTexts.json'


# get directory to descriptions file by competitor name
def get_directory_of_descriptions(name, entity_name):
    return './db/{}/domain_mining/search_results/'.format(entity_name) + name + '.json'


# get list of descriptions(documents) for one competitor
def extract_description_from_file(name, entity_name):
    # file_name_with_dir = get_directory_of_document_text(name, entity_name)
    # f = open(file_name_with_dir, encoding='utf-8')
    #
    # data = json.load(f)['descriptions']
    ans = []
    # idx = 0
    # for description in data:
    #     if description == 'lol':
    #         ans.append(description)
    #     else:
    #         f_2 = open(get_directory_of_descriptions(name, entity_name), encoding='utf-8')
    #         json_ = json.load(f_2)
    #         results = json_['results']
    #         result = results[idx]
    #         description_from_mother = result['description']
    #         ans.append(description_from_mother)
    #     idx += 1
    f_2 = open(get_directory_of_descriptions(name, entity_name), encoding='utf-8')
    json_ = json.load(f_2)
    # print(json_)
    results = json_['results']
    # print(results)
    for res in results:
        ans.append(res['description'])
    return ans




# get phrases list from one description(document)
def phrase_from_one_description(description, competitors_list, entity_name):
    # We collect words using nltk
    # print('phrase_from_one_description')
    words_list = nltk.pos_tag(nltk.word_tokenize(description))
    results = set()
    for i in range(len(words_list)-1):
        # They have format [word, pos]: [ 'banana', 'NN']
        first_word_info = list(words_list[i])
        second_word_info = list(words_list[i+1])

        first_word, first_word_pos = first_word_info
        second_word, second_word_pos = second_word_info
        first_word = first_word.lower()
        second_word = second_word.lower()

        if is_word(first_word) and not has_intersection(first_word, competitors_list, entity_name) :
            # If first word is noun add it to phrase list
            if first_word_pos in ['NN', 'NNP', 'VP','NNS', 'NNPS','NNP',] and len(first_word) > 3:
                if first_word_pos in ['NNS', 'NNPS'] and (first_word[-1]=='s'):
                    first_word = first_word[0:len(first_word) - 1]
                results.add(first_word)
            # If it is phrase that is like adjective + noun, add it as two words phrase
            if first_word_pos in ['VBG', 'JJ', 'NN', 'NNP', 'VP'] and second_word_pos in ['NN', 'NNP', 'VP', 'NNS','NNPS']:
                if is_word(second_word) and not has_intersection(second_word, competitors_list, entity_name):
                    if second_word_pos in ['NNS', 'NNPS','NNP','VBZ'] and (second_word[-1]=='s'):
                        second_word = second_word[0:len(second_word)-1]
                    results.add((first_word+' '+second_word))

    return filterize(list(results))


def phrases_from_descriptions_list(descriptions, competitors_list, entity_name):
    # print('Getting phrases from one competitor descriptions list')
    result = set()
    for description in descriptions:
        phrases = phrase_from_one_description(description,competitors_list,entity_name)
        for phrase in phrases:
            result.add(phrase)
    return list(result)


# Here we send a list of descriptions list [ [], [], [] ] to make one array []
def get_descriptions_list(descriptions_all):
    return list(numpy.concatenate(descriptions_all))


def phrase_frequency(phrase, descriptions_list):
    text = ' '.join(descriptions_list)
    # print('phrase_frequency')
    # descriptions_word_array = nltk.word_tokenize(text.lower())
    # return descriptions_word_array.count(phrase.lower())
    return len(re.findall(r'\b{}\b'.format(phrase), ' '.join(text.lower())))


def document_frequency(phrase, descriptions_list):
    # print('Getting document frequency')
    cnt = 0
    for description in descriptions_list:
        if len(re.findall(r'\b{}\b'.format(phrase), description)) > 0:
            cnt += 1
    return cnt


def phrase_length(phrase):
    # print('Getting phrase length')
    return len(phrase.lower().split(' '))


def average_distance(phrase, entity_name, descriptions_list_mapped):
    # print('Getting average distance')
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
                return 1000000000

    if n == 0:
        return 10000000

    return sum/(2*n)


# TODO implement this function
def cluster_entropy(phrase,descriptions_list):
    # arr = nltk.pos_tag(nltk.word_tokenize(description))
    C = []
    for desc in descriptions_list:
        if(phrase in desc):
            C.append(desc)


def phrase_independence(phrase, descriptions_list):
    # print('Getting phrase independence')
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








entity_name = 'Python'
# entity_name = 'Toyota'
# Extracting files
c = extract_description_from_file('c',entity_name)
php = extract_description_from_file('php', entity_name)
java = extract_description_from_file('java', entity_name)
javascript = extract_description_from_file('javascript',entity_name)
js = extract_description_from_file('js',entity_name)
go = extract_description_from_file('go', entity_name)
r = extract_description_from_file('r', entity_name)
matlab = extract_description_from_file('matlab', entity_name)
ruby = extract_description_from_file('ruby', entity_name)


# chevrolet = extract_description_from_file('chevrolet', entity_name)
# competition = extract_description_from_file('competition',entity_name)
# ford = extract_description_from_file('ford',entity_name)
# frontier = extract_description_from_file('frontier', entity_name)
# honda = extract_description_from_file('honda', entity_name)
# hybrid = extract_description_from_file('hybrid', entity_name)
# lexus= extract_description_from_file('lexus', entity_name)
# subaru = extract_description_from_file('subaru', entity_name)

descriptions_list_mapped = {
    # 'chevrolet': chevrolet,
    # 'competition': competition,
    # 'ford': ford,
    # 'honda': honda,
    # 'lexus': lexus,
    # 'subaru': subaru,
    # 'frontier': frontier,
    # 'hybrid': hybrid,

    'php': php,
    'javascript': javascript,
    'go': go,
    'r': r,
    'matlab': matlab,
    'ruby': ruby,
    'js': js,
    'c': c
}



competitors_list = list(descriptions_list_mapped.keys())
lists_of_descriptions_of_each_competitor = list(descriptions_list_mapped.values())
descriptions_list = get_descriptions_list(lists_of_descriptions_of_each_competitor)


list_of_phrases = phrases_from_descriptions_list(descriptions_list,competitors_list, entity_name )

resulting_dictionary = {}
idx = 0
print(len(list_of_phrases))
for phrase in list_of_phrases:
    idx += 1
    # print(idx, phrase)
    resulting_dictionary[phrase] = phrase_frequency(phrase, descriptions_list) * 0.138
    resulting_dictionary[phrase] += document_frequency(phrase, descriptions_list) * 0.06
    resulting_dictionary[phrase] += phrase_length(phrase) * 0.229
    resulting_dictionary[phrase] += average_distance(phrase, entity_name, descriptions_list_mapped) * (-0.073)
    resulting_dictionary[phrase] += phrase_independence(phrase, descriptions_list) * 0.187


# Sorting
resulting_dictionary = dict(sorted(resulting_dictionary.items(), key=lambda item: item[1], reverse=True))

most_ranked = list(resulting_dictionary.keys())[0:30]
for item in most_ranked:
    print(item)