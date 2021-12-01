import re
from bs4 import BeautifulSoup
from urllib.request import urlopen


def is_word(word):
    # return re.match(word, "[a-zA-Z]+")
    if(len(word) > 20 or len(word) < 3):
        return False
    for i in word:
        if i not in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM':
            return False
    return True


# Filtering the phrase that is entity or competitor name
def has_intersection(phrase, competitors_list, entity_name):
    entity_name = entity_name.lower()
    phrase = phrase.lower()
    if entity_name in phrase or phrase in entity_name:
        return True
    for competitor in competitors_list:
        if len(competitor) > 2 and competitor.lower() in phrase.lower():
            return True
        if len(phrase) > 2 and phrase.lower() in competitor.lower():
            return True
    return False


# minimum distance between w1 and w2 in s
def distance(s, w1, w2):
    s = s.lower()
    w1 = w1.lower()
    w2 = w2.lower()
    if w1 == w2:
        return 0

    words = s.split(" ")

    min_dist = len(words) + 1

    for index in range(len(words)):

        if words[index] == w1:
            for search in range(len(words)):

                if words[search] == w2:
                    curr = abs(index - search) - 1
                    if curr < min_dist:
                        min_dist = curr
    return min_dist


def reformat(text):
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = ''.join(chunk for chunk in chunks if chunk)
    return text



def get_text_from_link(url):
    try:
        html = urlopen(url, timeout=2).read()
        soup = BeautifulSoup(html, features="html.parser")
        
        # kill all script and style elements
        for script in soup(["script", "style","button","aside","nav",'input',"a",'footer','header',
                            'noscript','dialog','head','address','select','option']):
            script.extract()  # rip it out

        # get text
        text =  [t for t in soup.find_all(text=True) if t.parent.name in ['p','li']]
        # break into lines and remove leading and trailing space on each

        print('works')
        return ".".join(text)
    except:
        print('errored')
        return ''