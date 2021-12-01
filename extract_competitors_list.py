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

# Function returns list from list of tuples, when we use h1, h2, h3 patterns
def extractor_from_h_pattern(array_of_tuples):
    ans = list()
    for tuple in array_of_tuples:
        for item in tuple:
            word_arr = [word for word in item.strip().split(' ') if word not in ['or', 'and', '']]
            if not (' '.join(word_arr) == ''):
                ans.append(' '.join(word_arr))
    return ans


# Function that extract words that matches by pattern C1: competitor_name versus entity_name
def extract_c1(words, entity_name):
    wordsFormat = " ".join(words)

    results = re.findall(r'(\b[A-Z][a-zA-Z]*\b \b[A-Z][a-zA-Z]*\b|\b[A-Z][a-zA-Z]*\b) (vs|VS|Vs|versus)\.? {}'.format(entity_name), wordsFormat)
    ans = list(map(get_first_element, results))
    return filter_stop_words(ans)


# Function that extract words that matches by pattern C2: entity_name versus competitor_name
def extract_c2(words, entity_name):
    wordsFormat = " ".join(words)
    results = re.findall(r'{} (vs|VS|Vs|versus)\.? (\b[A-Z][a-zA-Z]*\b|\b[A-Z][a-zA-Z]*\b \b[A-Z][a-zA-Z]*\b)'.format(entity_name),
                         wordsFormat)
    ans = list(map(get_second_element, results))
    return filter_stop_words(ans)


# Function that extract words that matches by pattern C3
def extract_c3(words, entity_name):
    wordsFormat = " ".join(words)
    results = re.findall(r'{} or (\b[A-Z][a-zA-Z]*\b)'.format(entity_name), wordsFormat)
    return filter_stop_words(results)


# Function that extract words that matches by pattern C4
def extract_c4(words, entity_name):
    wordsFormat = " ".join(words)
    # results = re.findall(r'(\b[A-Z][a-zA-Z]+\b) or {}'.format(entity_name), wordsFormat)
    results = re.findall(r'(\b[A-Z][a-zA-Z]*\b) or {}'.format(entity_name), wordsFormat)
    return filter_stop_words(results)


# Function that extract words that matches by pattern H1
def extract_h1(words, entity_name):
    wordsFormat = " ".join(words)
    arr = re.findall(r'such as {},? (\b[A-Z][a-zA-Z]*\b \b[A-Z][a-zA-Z]*\b|\b[A-Z][a-zA-Z]*\b)( or (\b[A-Z][a-zA-Z]*\b)| and (\b[A-Za-z]*\b) (\b[A-Z][a-zA-Z]*\b)| and (\b[A-Z][a-zA-Z]*\b)|\b)|,(\b[A-Za-z])(\b[A-Z][a-zA-Z]*\b)| , (\b[A-Za-z]*\b)'.format(entity_name),wordsFormat)

    arr = extractor_from_h_pattern(arr)
    return filter_stop_words(arr)


# Function that extract words that matches by pattern H2
def extract_h2(words, entity_name):
    wordsFormat = " ".join(words)
    arr = re.findall(r'especially {},?( ([A-Z][a-zA-Z]*\b) (\b[A-Z][a-zA-Z]*\b)| (\b[A-Z][a-zA-Z]*\b)|\b)( and (\b[A-Z][a-zA-Z]*\b) (\b[A-Z][a-zA-Z]*\b)| and (\b[A-Z][a-zA-Z]*\b)|\b)'.format(entity_name), wordsFormat)
    arr = extractor_from_h_pattern(arr)
    return filter_stop_words(arr)



# Function that extract words that matches by pattern H3
def extract_h3(words, entity_name):
    wordsFormat = " ".join(words)
    arr = re.findall(r'including {},?( ([A-Z][a-zA-Z]*\b) (\b[A-Z][a-zA-Z]*\b)| (\b[A-Z][a-zA-Z]*\b)|\b)( and (\b[A-Z][a-zA-Z]*\b) (\b[A-Z][a-zA-Z]*\b)| and (\b[A-Z][a-zA-Z]*\b)|\b)'.format(entity_name), wordsFormat)
    arr = extractor_from_h_pattern(arr)
    return filter_stop_words(arr)


# Function that reads file of search results and extracts fields "title" and "snippet"
def extract_titles_and_snippets(file_name):
    f = open(file_name, encoding='utf-8')
    data = json.load(f)
    titleAndSnippets = []
    for item in data:
        if 'items' in data[item]:
            for item in data[item]['items']:
                t = item['title']
                s = item['snippet']

                # titleAndSnippets.append(item['title'])
                titleAndSnippets.append(s+t)

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


# calculate match count of one competitor in a competitor_list(pattern) multiplied by weight(pattern)
def calculate_match_count_util(competitors_extracted_by_some_pattern, pattern_weight, current_competitor):
    return pattern_weight * competitors_extracted_by_some_pattern.count(current_competitor)
1

# as we will work with each extracted competitor to check it, we need to have a unique set of them.
def get_unique_competitors(competitors_list_dict):
    return list(set(list(numpy.concatenate(list(competitors_list_dict.values())))))

# calculate match count for given competitor_name from search results
def calculate_match_count(competitors_list_dict, competitor):
    cnt = 0
    for item in competitors_list_dict.keys():
        if item in ['C1', 'C2']:
            cnt += calculate_match_count_util(competitors_list_dict[item], 5, competitor)
        else:
            cnt += calculate_match_count_util(competitors_list_dict[item], 1, competitor)
    return cnt


# calculate pmi by this formula: hits(e,c)/(hits(c)*hits(e))
def pointwise_mutual_information(search_results, entity_name, competitor_name):
    wordsFormat = " ".join(search_results)

    # hits_ce is number of occurences of entity name and competitor name together in our search results
    hits_ce = len(re.findall(r'{entity_name} (and|or|,|vs|vs.|VS|Vs) {competitor_name}'.format(entity_name=entity_name, competitor_name=competitor_name), wordsFormat))
    hits_ce += len(re.findall(r'{competitor_name} (and|or|,|vs|vs.|VS|Vs) {entity_name}'.format(entity_name=entity_name, competitor_name=competitor_name), wordsFormat))
    # hits_c and hits_e is number of occurences of entity name or competitor name in our search results respectively
    hits_c = len(re.findall(r'\b{}\b'.format(competitor_name), wordsFormat)) + len(re.findall(r'[^a-zA-z]{}[^a-zA-z]'.format(competitor_name), wordsFormat))
    hits_e = len(re.findall(r'\b{}\b'.format(entity_name), wordsFormat))  + len(re.findall(r'[^a-zA-z]{}[^a-zA-z]'.format(entity_name), wordsFormat))
    return hits_ce / (hits_e * hits_c)

# calculate candidate confidence by following formula: match_count(competitor, entity) / hits(competitor)
def candidate_confidence(search_results, competitor_name, competitors_list_dict):
    wordsFormat = " ".join(search_results)
    hits_c = len(re.findall(r'\b{}\b'.format(competitor_name), wordsFormat)) + len(re.findall(r'[^a-zA-z]{}[^a-zA-z]'.format(competitor_name), wordsFormat))
    return calculate_match_count(competitors_list_dict, competitor_name) / hits_c

# returns finally rank score
def confidence_score(competitor_name, entity_name, competitors_list_dict, extracted_texts):
    search_results = numpy.concatenate(list(extracted_texts.values()))
    mc = 0.2 * calculate_match_count(competitors_list_dict, competitor=competitor_name)
    pmi = 0.6 * pointwise_mutual_information(search_results, entity_name, competitor_name)
    cc = 0.2 * candidate_confidence(search_results, competitor_name, competitors_list_dict)
    return mc + pmi + cc

# returns sorted list of results by rank, which is value of dictionary
def get_ranked_list_of_competitor_names(entity_name, competitors_list_dict, extracted_texts):
    competitors = get_unique_competitors(competitors_list_dict)
    CL = {}
    for competitor in competitors:
        if(entity_name.lower() not in competitor.lower()):
            CS = confidence_score(competitor, entity_name, competitors_list_dict, extracted_texts)
            CL[competitor] = CS
    # here we filter all results by translating to lowercase, because some competitor names occurs in different ways, e.g., "matlab, MATLAB, MatLab"
    competitors = list(map(lambda x: x.lower(), competitors))
    CL_New = {}
    for item in CL:
        if(item.lower() in competitors):
            if(item.lower() not in CL_New):
                CL_New[item.lower()] = CL[item]
            else:
                CL_New[item.lower()] += CL[item]

    return dict(sorted(CL_New.items(), key=lambda item: item[1], reverse=True))

# function use pointwise mutual information to check whether two words actually form a unique concept
def filter_competitor_names_bigrams(text, competitors_list):
    competitors_list_keys = list(competitors_list.keys())
    for i in range(len(competitors_list_keys)):
        competitor_name = competitors_list_keys[i]
        if ' ' in competitor_name:
            pairs = competitor_name.split(' ')
            if (len(pairs) != 2):
                continue
            first_word, second_word = pairs
            hits_as_pair = len(re.findall(r'{}'.format(competitor_name.lower()), text))
            hits_first = len(re.findall(r'[^a-zA-Z]{}[^a-zA-Z]'.format(first_word.lower()), text))
            hits_second = len(re.findall(r'[^a-zA-Z]{}[^a-zA-Z]'.format(second_word.lower()), text))

            pmi = hits_as_pair / (hits_first * hits_second)

            # logically if number of occurences as pair and separately are approximately very close to each other,
            # this pair of words express a precise, unique concept
            if (hits_as_pair / max(hits_first, hits_second) > 0.6):
                common = 1 / max(hits_as_pair, hits_first, hits_second)
                threshold = 0.7
                if pmi / common > threshold:
                    f_point, s_point = 0, 0
                    if first_word in competitors_list:
                        f_point = competitors_list[first_word]
                        del competitors_list[first_word]
                    if second_word in competitors_list:
                        s_point = competitors_list[second_word]
                        del competitors_list[second_word]
                    competitors_list[competitor_name] += (f_point + s_point)
            else:
                del competitors_list[competitor_name]

    return dict(sorted(competitors_list.items(), key=lambda item: item[1], reverse=True))


# main function
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

    all_text = " ".join(list(numpy.concatenate(list(extracted_texts.values())))).lower()

    # here we used pmi to filter competitor names to whether two words actually form a unique concept
    wws = filter_competitor_names_bigrams(all_text, ranked_CL)
    print(list(map(lambda x: x.capitalize(), list(wws)[0:10])))


names = [
    # 'Prada',
    # 'Python',
    # 'Toyota',
    # 'Adidas',
    # 'Twix'
    'Amazon',
    # 'Facebook'
]
for entity_name in names:
    work(entity_name)