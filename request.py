import json

from utils.helpers import get_text_from_link


def extract_links_from_file(file_name):
    f = open("./db/Python/domain_mining/competitor_list/"+file_name+'.json', encoding='utf-8')
    results = json.load(f)['results']
    links = []
    for res in results:
        links.append(res['link'])
    return links


c = extract_links_from_file('c')
php = extract_links_from_file('php')
java = extract_links_from_file('java')
javascript = extract_links_from_file('javascript')
js = extract_links_from_file('js')
go = extract_links_from_file('go')
r = extract_links_from_file('r_')
matlab = extract_links_from_file('matlab')
ruby = extract_links_from_file('ruby')


links_list_mapped = {
    'c': c,
    'php': php,
    'java': java,
    'javascript': javascript,
    'go': go,
    'r': r,
    'matlab': matlab,
    'ruby': ruby,
    'js': js
}

for c_name in links_list_mapped:
    print("WORKING ON "+ c_name)
    links = links_list_mapped[c_name]
    documentTextList = []
    for link in links:
        documentText = get_text_from_link(link)
        documentTextList.append(documentText)
    with open('{}_documentTexts.json'.format(c_name), 'w',encoding='UTF-8') as f:
        json.dump({'descriptions':documentTextList}, f,ensure_ascii=False, indent=4)
