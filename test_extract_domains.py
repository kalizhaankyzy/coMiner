import json
import math
import nltk
import numpy
import re
from utils.helpers import is_word, has_intersection, distance, word_is_in_text
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
# def get_directory_of_document_text(name, entity_name):
#     return './db/{}/domain_mining/document_texts/'.format(entity_name) + name + '_documentTexts.json'


# get directory to descriptions file by competitor name
def get_directory_of_descriptions(name, entity_name):
    return './db/{}/domain_mining/search_results/'.format(entity_name) + name + '.json'


# get list of descriptions(documents) for one competitor
def extract_description_from_file(name, entity_name):
    ans = []
    f_2 = open(get_directory_of_descriptions(name, entity_name), encoding='utf-8')
    json_ = json.load(f_2)
    results = json_['results']
    for res in results:
        ans.append(res['description'])
    return ans


# get phrases list from one description(document)
def phrase_from_one_description(description, competitors_list, entity_name):
    # We collect words using nltk
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
            if first_word_pos in ['NN','NNP',] and len(first_word) > 3:
                results.add(first_word)
            # If it is phrase that is like adjective + noun, add it as two-word phrase
            if first_word_pos in ['VBG', 'JJ', 'NN', 'NNP', 'VP'] and second_word_pos in ['NN', 'NNP', 'VP']:
                if is_word(second_word) and not has_intersection(second_word, competitors_list, entity_name):
                    results.add(first_word+' '+second_word)

    return filterize(list(results))

# returns unique list of descriptions
def phrases_from_descriptions_list(descriptions, competitors_list, entity_name):
    result = set()
    for description in descriptions:
        phrases = phrase_from_one_description(description, competitors_list, entity_name)
        for phrase in phrases:
            result.add(phrase)
    return list(result)


# Here we send a list of descriptions list [ [], [], [] ] to make one array []
def get_descriptions_list(descriptions_all):
    return list(numpy.concatenate(descriptions_all))

# returns frequency of phrase in document
def phrase_frequency(phrase, descriptions_list):
    text = ' '.join(descriptions_list)

    return len(re.findall(r'\b{}\b'.format(phrase), text.lower())) + len(re.findall(r'[^a-zA-z]{}[^a-zA-z]'.format(phrase), text.lower()))

# returns the number of documents containing the phrase
def document_frequency(phrase, descriptions_list):
    cnt = 0
    for description in descriptions_list:
        if len(re.findall(r'[^a-zA-z]{}[^a-zA-z]'.format(phrase), description)) > 0:
            cnt += 1
    return cnt

# Getting phrase length
def phrase_length(phrase):
    return len(phrase.lower().split(' '))

# it is calculated by the distance between the phrase and the given entity or its competitors
def average_distance(phrase, entity_name, descriptions_list, competitors_list):
    sum = 0
    n = 0
    for c_name in competitors_list:
        for description in descriptions_list:
            description = description.lower()
            phrase = phrase.lower()
            try:
                if re.search(r'\b{}\b'.format(phrase, description)) != None:
                # if re.search(r'\W' + phrase + r'\W', description) != None:
                    if ' ' in phrase:
                        p_new = phrase.replace(" ", '')
                        description = description.replace(phrase, p_new)
                        phrase = p_new

                    sum += (distance(description, entity_name, phrase) + distance(description, c_name, phrase))
                    n += 1
            except:
                return 1000000000
        if n == 0:
            return 1000000000

        return sum / (2 * n)


def cluster_entropy(phrase, descriptions_list, domain_list):
    documents_with_phrase = []
    CE = 0

    for description in descriptions_list:
        if (word_is_in_text(phrase, description)):
            documents_with_phrase.append(description.lower())

    for term in domain_list:
        documents_with_term = []
        for description in descriptions_list:
            if (word_is_in_text(term, description)):
                documents_with_term.append(description.lower())
        divisible = len(list((set(documents_with_phrase).intersection(set(documents_with_term)))))
        divider = len(documents_with_phrase)
        if divider == 0:
            divider = 1
        probability = divisible / divider
        log_value = 0
        if probability != 0:
            log_value = math.log2(probability)
        CE += (probability * log_value)
    # print(phrase, - CE)
    return -CE


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

def extract_domains(entity, competitor):
    # print(extract_description_from_file(competitor.lower(), entity))
    descriptions = list()
    descriptions.append(extract_description_from_file(competitor.lower(), entity))
    descriptions_list = get_descriptions_list(descriptions)

    list_of_phrases = phrases_from_descriptions_list(descriptions_list, competitors_list, entity_name)
    print(len(list_of_phrases))
    resulting_dictionary = {}

    for phrase in list_of_phrases:
        resulting_dictionary[phrase] = phrase_frequency(phrase, descriptions_list) * 0.138
        resulting_dictionary[phrase] += document_frequency(phrase, descriptions_list) * 0.06
        resulting_dictionary[phrase] += phrase_length(phrase) * 0.229
        resulting_dictionary[phrase] += average_distance(phrase, entity_name, descriptions_list, competitors_list) * (
            -0.073)
        resulting_dictionary[phrase] += phrase_independence(phrase, descriptions_list) * 0.187
        resulting_dictionary[phrase] += cluster_entropy(phrase, descriptions_list, list_of_phrases) * 0.103

    resulting_dictionary = dict(sorted(resulting_dictionary.items(), key=lambda item: item[1], reverse=True))
    return list(resulting_dictionary.keys())[0:5]

entity_and_competitors = {
    'Adidas':{
        'Nike',
        'Puma',
        'Pace',
        'Advantage',
        'Footjoy',
        'Legacy lifter',
        'Converse',
        'Reebok',
        'Position',
        'Everybody'
    },
    'Python': {
        'R',
        'Java',
        'Javascript',
        'C',
        'Ruby',
        'Matlab',
        'Php',
        'Gatoroid',
        'Go',
        'Golang'
    },
    'Twix':{
        'Right',
        'Snickers',
        'Kit kat',
        'Left',
        'Mars',
        'Treat',
        'Reese',
        'Aldi',
        'Carmel',
        'Donut'
    },
    'Prada': {
        'Gucci',
        'Louis vuitton',
        'Fendi',
        'Miu miu',
        'Chanel',
        'Versace',
        'Rajput',
        'Nada',
        'Azam',
        'Chloe'
    },
    'Toyota': {
        'Honda',
        'Nissan',
        'Competition',
        'Chevrolet',
        'Subaru',
        'Lexus',
        'Ford',
        'Volkswagen',
        'Kia',
        'Tesla'
    },
    'Facebook':{
        'Instagram', 
        'Twitter', 
        'Google', 
        'Apple', 
        'Youtube', 
        'Linkedin', 
        'Snapchat', 
        'Twitch', 
        'Australia', 
        'Whatsapp'
    },
    'Amazon':{
        'Walmart', 
        'Google', 
        'Apple', 
        'Shopify', 
        'Microsoft', 
        'Alibaba', 
        'Netflix', 
        'Prime', 
        'Hachette', 
        'Youtube'
    }
}

for entity_name in entity_and_competitors.keys():
    print("Entity: ",entity_name)
    competitors_list = list(entity_and_competitors[entity_name])
    for competitor in competitors_list:
        print("Competitor: ", competitor)
        for item in extract_domains(entity_name, competitor):
            print(item)
        print("-"*15)