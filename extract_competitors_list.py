import json
import re
import numpy
from nltk.corpus import stopwords

stop_words = stopwords.words('english')


# Filter words in array of words using nltk
def filter_stop_words(arr):
    ans = []
    for word in arr:
        if word.lower() not in stop_words:
            ans.append(word)
    return ans

def get_first_element(arr):
    return arr[0]


def get_second_element(arr):
    return arr[1]


# Function that extract words that matches by pattern C1: competitor_name versus entity_name
def extract_c1(words, entity_name):
    wordsFormat = " ".join(words)
    results = re.findall(r'(\b[A-Z][a-zA-Z]*\b) (vs|VS|Vs|versus)\.? {}'.format(entity_name), wordsFormat)
    # print(results)

    ans = list(map(get_first_element, results))
    return filter_stop_words(ans)


# Function that extract words that matches by pattern C2: entity_name versus competitor_name
def extract_c2(words, entity_name):
    wordsFormat = " ".join(words)
    results = re.findall(r'{} (vs|VS|Vs|versus)\.? (\b[A-Z][a-zA-Z]*\b)'.format(entity_name),
                         wordsFormat)

    ans = list(map(get_second_element, results))
    # print( ans)
    return filter_stop_words(ans)


# Function that extract words that matches by pattern C3
def extract_c3(words, entity_name):
    wordsFormat = " ".join(words)
    results = re.findall(r'{} or (\b[A-Z][a-zA-Z]*\b)'.format(entity_name), wordsFormat)
    # print(results)
    return filter_stop_words(results)


# Function that extract words that matches by pattern C4
def extract_c4(words, entity_name):
    wordsFormat = " ".join(words)
    results = re.findall(r'(\b[A-Z][a-zA-Z]*\b) or {}'.format(entity_name), wordsFormat)
    # print(results)
    return filter_stop_words(results)


# Function that extract words that matches by pattern H1
def extract_h1(words, entity_name):
    wordsFormat = " ".join(words)

    arr = re.findall(r'such as {},? (\b[A-Z][a-zA-Z]*\b \b[A-Z][a-zA-Z]*\b|\b[A-Z][a-zA-Z]*\b)'.format(entity_name), wordsFormat)
    #
    # such as {},? (\b[A-Z][a-zA-Z]*\b \b[A-Z][a-zA-Z]*\b|\b[A-Z][a-zA-Z]*\b)( or (\b[A-Z][a-zA-Z]*\b)| and (\b[A-Za-z]*\b) (\b[A-Z][a-zA-Z]*\b)| and (\b[A-Z][a-zA-Z]*\b)|\b)
    # print(arr)
    return filter_stop_words(extract_h1(arr))


# Function that extract words that matches by pattern H2
def extract_h2(words, entity_name):
    wordsFormat = " ".join(words)
    arr = re.findall(r'especially {}(, ([A-Z][a-zA-Z]*\b) (\b[A-Z][a-zA-Z]*\b)|, (\b[A-Z][a-zA-Z]*\b)|\b)( and (\b[A-Z][a-zA-Z]*\b) (\b[A-Z][a-zA-Z]*\b)| and (\b[A-Z][a-zA-Z]*\b)|, and (\b[A-Z][a-zA-Z]*\b) (\b[A-Z][a-zA-Z]*\b)|, and (\b[A-Z][a-zA-Z]*\b)|\b)'.format(entity_name), wordsFormat)
    print(arr)
    arr = re.findall(r'especially {},? (\b[A-Z][a-zA-Z]*\b \b[A-Z][a-zA-Z]*\b|\b[A-Z][a-zA-Z]*\b)'.format(entity_name), wordsFormat)
    print(arr)

    return filter_stop_words(arr)


# Function that extract words that matches by pattern H3
def extract_h3(words, entity_name):
    wordsFormat = " ".join(words)
    arr = re.findall(r'including {},? (\b[A-Z][a-zA-Z]+\b)'.format(entity_name), wordsFormat)

    return filter_stop_words(arr)


# Function that reads file of search results and extracts fields "title" and "snippet"
def extract_titles_and_snippets(file_name):
    f = open(file_name, encoding='utf-8')
    data = json.load(f)
    titleAndSnippets = []
    for item in data:
        if 'items' in data[item]:
            for item in data[item]['items']:
                titleAndSnippets.append(item['title'])
                titleAndSnippets.append(item['snippet'])

    f.close()
    return titleAndSnippets


# create a dictionary of extracted words for each pattern
def get_competitor_list_dict_from_extracted_texts_dict(extracted_texts, entity_name):
    competitors_list_dict = {
        'C1': extract_c1(extracted_texts['C1'], entity_name),
        'C2': extract_c2(extracted_texts['C2'], entity_name),
        'C3': extract_c3(extracted_texts['C3'], entity_name),
        'C4': extract_c4(extracted_texts['C4'], entity_name),
        'H1': extract_h1(extracted_texts['H1'], entity_name),
        'H2': extract_h2(extracted_texts['H2'], entity_name),
        'H3': extract_h3(extracted_texts['H3'], entity_name)}
    return competitors_list_dict


# calculate math count of one competitor in a competitors_list(pattern) multiplied by weight(pattern)
def calculate_math_count_util(competitors_extracted_by_some_pattern, pattern_weight, current_competitor):
    return pattern_weight * competitors_extracted_by_some_pattern.count(current_competitor)


# as we will work with each extracted competitor to check it, we need to have a unique set of them.
def get_unique_competitors(competitors_list_dict):
    return list(set(list(numpy.concatenate(list(competitors_list_dict.values())))))


# returns dictionary of math count (with weights) for each candidate competitor { CN[i]:mc(CN[i]),.... }
def calculate_math_count(competitors_list_dict):
    unique_competitors = get_unique_competitors(competitors_list_dict)
    res = dict()

    for competitor in unique_competitors:
        res[competitor] = calculate_math_count_util(competitors_list_dict['C1'], 5, competitor)
        res[competitor] += calculate_math_count_util(competitors_list_dict['C2'], 5, competitor)
        res[competitor] += calculate_math_count_util(competitors_list_dict['C3'], 1, competitor)
        res[competitor] += calculate_math_count_util(competitors_list_dict['C4'], 1, competitor)
        res[competitor] += calculate_math_count_util(competitors_list_dict['H1'], 1, competitor)
        res[competitor] += calculate_math_count_util(competitors_list_dict['H2'], 1, competitor)
        res[competitor] += calculate_math_count_util(competitors_list_dict['H3'], 1, competitor)
    return res


# here search_results is array of snippets and titles
def pointwise_mutual_information(search_results, entity_name, competitor_name):
    wordsFormat = " ".join(search_results)
    cnt = 0
    for sentence in search_results:
        # print(sentence)
        # if (
        #     len(re.findall(r' {entity_name} [a-z][a-z] {competitor_name}'.format(entity_name=entity_name, competitor_name=competitor_name), sentence)) > 0
                # len(re.findall(r' {entity_name} [a-z][a-z] {competitor_name}'.format(entity_name=entity_name, competitor_name=competitor_name), sentence)) > 0
                # or len(re.findall(r' {competitor_name} [a-z][a-z] {entity_name}'.format(entity_name=entity_name, competitor_name=competitor_name), sentence)) > 0
                # or len(re.findall(r' {competitor_name} [a-z][a-z][a-z] {entity_name}'.format(entity_name=entity_name, competitor_name=competitor_name),sentence)) > 0
                # or len(re.findall(r' {competitor_name} [a-z][a-z][a-z] {entity_name}'.format(entity_name=entity_name, competitor_name=competitor_name), sentence)) > 0
        # ):
            # print(len(re.findall(r' {entity_name} [a-z][a-z] {competitor_name}'.format(entity_name=entity_name, competitor_name=competitor_name), sentence)))

        cnt += len(re.findall(r' {entity_name} [a-z][a-z] {competitor_name}'.format(entity_name=entity_name, competitor_name=competitor_name), sentence))
        cnt += len(re.findall(r' {competitor_name} [a-z][a-z] {entity_name}'.format(entity_name=entity_name, competitor_name=competitor_name), sentence))
        cnt += len(re.findall(r' {competitor_name} [a-z][a-z] {entity_name}'.format(entity_name=entity_name, competitor_name=competitor_name), sentence))
        cnt += len(re.findall(r' {competitor_name} [a-z][a-z][a-z] {entity_name}'.format(entity_name=entity_name, competitor_name=competitor_name), sentence))


    hits_ce = cnt
    # print(cnt)
    hits_c = len(re.findall(r'\b{}(\b)'.format(competitor_name), wordsFormat))
    hits_e = len(re.findall(r'\b{}\b'.format(entity_name), wordsFormat))
    return hits_ce / (hits_e * hits_c)


def candidate_confidence(search_results, competitor_name, competitors_list_dict):
    wordsFormat = " ".join(search_results)
    return calculate_math_count(competitors_list_dict)[competitor_name] / len(
        re.findall(r'\b{}\b'.format(competitor_name), wordsFormat))


def confidence_score(competitor_name, entity_name, competitors_list_dict, extracted_texts):
    search_results = numpy.concatenate(list(extracted_texts.values()))
    r = calculate_math_count(competitors_list_dict)
    k1 = 0.2 * r.get(competitor_name)
    # k1 = 0
    k2 = 0.6 * pointwise_mutual_information(search_results, entity_name, competitor_name)
    # print(competitor_name,pointwise_mutual_information(search_results, entity_name, competitor_name))
    k3 = 0.2 * candidate_confidence(search_results, competitor_name, competitors_list_dict)
    return k1 + k2 + k3


def get_ranked_list_of_competitor_names(entity_name, competitors_list_dict, extracted_texts):
    competitors = get_unique_competitors(competitors_list_dict)
    CL = {}
    for competitor in competitors:
        CS = confidence_score(competitor, entity_name, competitors_list_dict, extracted_texts)
        CL[competitor] = CS
    return dict(sorted(CL.items(), key=lambda item: item[1], reverse=True))


def work(entity_name):
    DB_ROOT = 'db/{}/competitor_list/'.format(entity_name)
    extracted_texts = {
        'C1': extract_titles_and_snippets(DB_ROOT + 'c1.json'),
        'C2': extract_titles_and_snippets(DB_ROOT + 'c2.json'),
        'C3': extract_titles_and_snippets(DB_ROOT + 'c3.json'),
        'C4': extract_titles_and_snippets(DB_ROOT + 'c4.json'),
        'H1': extract_titles_and_snippets(DB_ROOT + 'h1.json'),
        'H2': extract_titles_and_snippets(DB_ROOT + 'h2.json'),
        'H3': extract_titles_and_snippets(DB_ROOT + 'h3.json')
    }
    competitors_list_for_each_pattern = get_competitor_list_dict_from_extracted_texts_dict(extracted_texts, entity_name)
    ranked_CL = get_ranked_list_of_competitor_names(entity_name, competitors_list_for_each_pattern, extracted_texts)

    print(ranked_CL)
    # print(list(ranked_CL)[0:9])


names = [
    # 'Python',
    'Prada',
    # 'Toyota',
    # 'Adidas'
]
for entity_name in names:
    work(entity_name)
