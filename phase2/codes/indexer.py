import os
import os.path
import sys
import xml.sax
import re
from collections import defaultdict
from nltk.corpus import stopwords
import Stemmer
import time

ps = Stemmer.Stemmer('english')
stop_words = set(stopwords.words('english'))
stop_words_url = set(["http", "https", "www", "ftp", "com", "net",
                      "org", "archives", "pdf", "html", "png", "txt", "redirect"])

# idf = defaultdict(list)
idf = {}
tf = defaultdict(dict)
stems = {}
TOTAL_TOKENS = 0
doc_data = {}


def tokenize(text):
    return(re.split(r'\W+', text))


def stem(text, did):
    global TOTAL_TOKENS

    stemmed_sentence = []
    for i in tokenize(text):
        TOTAL_TOKENS += 1
        if i == "" or not i:
            continue

        if i not in stop_words and i not in stop_words_url:
            if i not in stems:

                stems[i] = ps.stemWord(i)
                idf[stems[i]] = defaultdict(int)

            stemmed_sentence.append(stems[i])
            idf[stems[i]][did] += 1
            if idf[stems[i]][did] == 1:
                idf[stems[i]]['total'] += 1
    # print(stemmed_sentence)
    return stemmed_sentence


def fillTable(text, ind, did):
    words = stem(text, did)
    for w in words:
        if tf[w] == {}:
            tf[w]['total'] = idf[w]['total']
        if did not in tf[w].keys():
            tf[w][did] = [0 for i in range(7)]

        tf[w][did][ind] += 1
        tf[w][did][0] += 1


def createTF(text, did, title):
    t = title.lower()
    b = ''
    i = ''
    r = ''
    l = ''
    c = ''
    lines = text.split('\n')
    ref_flag = 0
    info_flag = 0
    for line in lines:
        if not line:
            continue
        line = line.lower()

        if ref_flag == 0:
            if re.search(r"==\s*references\s*==", line):
                ref_flag = 1
                continue
            b += line
            b += ' '
            if re.search(r'\{\{\s*infobox', line):
                i = re.sub(r'\{\{\s*infobox(.*)', r'\1', line)
                i += ' '
                info_flag = 1
            elif info_flag == 1:
                if re.search(r'\s*\}\}\s*', line):
                    info_flag = 0
                    continue
                else:
                    i += line
                    i += ' '
        elif ref_flag == 1:
            if ("[[category" in line) or ("==" in line) or ("defaultsort" in line):
                ref_flag = 2
                continue
            r += line
            r += ' '
        elif ref_flag == 2:
            # print(line[0])
            if line[0] == '*':
                l += line
                l += ''
            else:
                x = re.findall(r'.*category\s*:\s*(.*)\]\]', line)
                c += ''.join(x)
                c += ''

    fillTable(t, 1, did)
    fillTable(b, 2, did)
    fillTable(i, 3, did)
    fillTable(l, 4, did)
    fillTable(r, 5, did)
    fillTable(c, 6, did)


page_id = 0


class DocumentHandler(xml.sax.ContentHandler):
    def __init__(self):

        self.title = ''
        self.text = ''
        self.id = ''
        self.CurrentData = ''
        self.idDoc = 0
        # print('j')

    # Define the start

    def startElement(self, tag, attributes):
        self.CurrentData = tag

    def characters(self, content):
        if self.CurrentData == '':
            return
        if self.CurrentData == 'title':
            self.title += content
        elif self.CurrentData == 'text':
            self.text += content
        elif self.CurrentData == 'id' and self.idDoc == 0:
            self.id = content
            self.idDoc = 1

    def endElement(self, tag):
        global page_id
        if tag == 'page':
            
            doc_data[self.id] = ''.join(self.title.lower()).strip()
            createTF(self.text, self.id, self.title)
            self.title = ''
            self.text = ''
            self.id = ''
            self.CurrentData = ''
            self.idDoc = 0

            page_id += 1


# create an XMLReader
parser = xml.sax.make_parser()
# turn off namepsaces
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
# override the default ContextHandler
Handler = DocumentHandler()
parser.setContentHandler(Handler)
# parser.parse("../../ref/trial.xml")

t1 = time.time()

parser.parse(sys.argv[1])

t2 = time.time()

if not os.path.isdir(sys.argv[2]):
    os.mkdir(sys.argv[2])

keys = 0


with open(f'{sys.argv[2]}/tf.txt', 'a') as f:

    for w in tf:
        keys += 1
        doc = ''
        for docs in tf[w]:
            if docs == 'total':
                doc += str(docs)
                doc += ':'
                doc += str(tf[w][docs])
                doc += ';'
                continue

            doc += str(docs)
            doc += ':'
            
            for ind in range(7):
                tf[w][docs][ind] = str(tf[w][docs][ind])
            # print(tf[w][docs])
            doc += str(','.join(tf[w][docs]))
            doc += ';'
        # doc +='}'
        print(w, doc,  file=f)


with open(f'{sys.argv[2]}/docs.txt', 'a') as f:
    print(page_id,  file=f)
    for d in doc_data:
        print(d, doc_data[d],  file=f)

f = open(f'{sys.argv[3]}', 'a')
f.write(str(keys) + '\n')
f.close()
# for i in tf.keys():
#     print(i, tf[i])
print(page_id)
print('Time Taken in Seconds:', str(t2-t1))
