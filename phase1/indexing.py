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
index = defaultdict(dict)
stems = {}
# total_wsords = 0
TOTAL = 0
dataset = []


class InvertedIndexing():
    def __init__(self):
        pass

    def tokenize(self, text):
        return(re.split(r'\W+', text))

    def stem(self, text):
        global TOTAL
        stop_words = set(stopwords.words('english'))
        stop_words_url = set(["http", "https", "www", "ftp", "com", "net",
                              "org", "archives", "pdf", "html", "png", "txt", "redirect"])
        stemmed_sentence = []
        for i in self.tokenize(text):
            TOTAL += 1
            if i == "" or not i:
                continue

            if i not in stop_words and i not in stop_words_url:
                if i not in stems:

                    stems[i] = ps.stemWord(i)

                stemmed_sentence.append(stems[i])

        # print(stemmed_sentence)
        return stemmed_sentence

    def cleaning(self, body):
        # print(text)

        for i in body:
            tid = i[0]
            title = self.stem(i[1].lower())
            text = i[2]

            s = 'd' + tid
            doc = s
            for w in title:

                if len(w) <= 1:
                    continue
                if doc in index[w].keys():
                    if 't' in index[w][doc].keys():
                        index[w][doc]['t'] += 1
                    else:
                        index[w][doc]['t'] = 1
                else:
                    index[w][doc] = {'t': 1}
            text = text.lower()
            lines = text.split('\n')
            flag = 0
            reflag = 0
            bod = []
            for l in lines:
                # print(l)
                # chcek for references

                if reflag == 0:
                    # print(l)
                    # check for ending of body
                    if re.search(r"\s*==\s*references\s*==\s*", l):
                        reflag = 1
                        continue
                    # add body to index
                    # print(len(l))
                    bod = self.stem(l)
                    # print('yes', bod)
                    for w in bod:
                        if re.match(r'^[a-zA-Z]$', w):
                            # print('yes', w)
                            continue
                        if doc in index[w].keys():
                            if 'b' in index[w][doc].keys():
                                index[w][doc]['b'] += 1
                            else:
                                index[w][doc]['b'] = 1
                        else:
                            index[w][doc] = {'b': 1}
                    # check for infobox
                    if re.search(r'\{\{\s*infobox', l):
                        info = re.sub(r'\{\{\s*infobox(.*)', r'\1', l)
                        flag = 1
                        if not info:
                            pass
                        else:

                            infobox = self.stem(info[0])
                            for w in infobox:
                                if re.match(r'^[a-zA-Z]$', w):
                                    continue
                                if doc in index[w].keys():
                                    if 'i' in index[w][doc].keys():
                                        index[w][doc]['i'] += 1
                                    else:
                                        index[w][doc]['i'] = 1
                                else:
                                    index[w][doc] = {'i': 1}

                    # add info inside the infobox
                    elif flag == 1:
                        if re.search(r'\s*\}\}\s*', l):
                            flag = 0
                        else:
                            # info = re.sub(r'\{\{\s*infobox(.*)', r'\1', l)
                            info = l
                            # print('helo', info)
                            infobox = self.stem(info)
                            for w in infobox:
                                if re.match(r'^[a-zA-Z]$', w):
                                    continue
                                if doc in index[w].keys():
                                    if 'i' in index[w][doc].keys():
                                        index[w][doc]['i'] += 1
                                    else:
                                        index[w][doc]['i'] = 1
                                else:
                                    index[w][doc] = {'i': 1}
                else:
                    # Look for references
                    x = re.findall(r'.*\|title\s*=\s*([^\|]*)', l)

                    if not x:
                        # Look for External Links
                        x = re.findall(r'\*[\ ]*\[([^\]]*)', l)

                        if not x:
                            x = re.findall(r'.*category\s*:\s*(.*)\]\]', l)
                            if not x:
                                pass
                            else:
                                cat = x
                                # print(len(x))
                                cats = self.stem(cat[0])
                                for w in cats:
                                    if re.match(r'^[a-zA-Z]$', w):
                                        continue
                                    if doc in index[w].keys():
                                        if 'c' in index[w][doc].keys():
                                            index[w][doc]['c'] += 1
                                        else:
                                            index[w][doc]['c'] = 1
                                    else:
                                        index[w][doc] = {'c': 1}
                        else:
                            link = x
                            # print(len(link))
                            links = self.stem(link[0])
                            for w in links:
                                if re.match(r'^[a-zA-Z]$', w):
                                    continue
                                if doc in index[w].keys():
                                    if 'l' in index[w][doc].keys():
                                        index[w][doc]['l'] += 1
                                    else:
                                        index[w][doc]['l'] = 1
                                else:
                                    index[w][doc] = {'l': 1}
                    else:
                        ref = x
                        # print(len(ref))
                        refs = self.stem(ref[0])
                        for w in refs:
                            if re.match(r'^[a-zA-Z]$', w):
                                continue
                            if doc in index[w].keys():
                                if 'r' in index[w][doc].keys():
                                    index[w][doc]['r'] += 1
                                else:
                                    index[w][doc]['r'] = 1
                            else:
                                index[w][doc] = {'r': 1}

        # return (bod, infobox, refs, cats, links)


class DocumentHandler(xml.sax.ContentHandler):
    def __init__(self):

        self.title = ''
        self.text = ''
        self.id = ''
        self.CurrentData = ''
        self.idDoc = 0

    # Define the start

    def startElement(self, tag, attributes):
        self.CurrentData = tag

    def characters(self, content):
        if self.CurrentData == '':
            return
        # print(self.CurrentData)
        if self.CurrentData == 'title':
            self.title += content
            # print(self.title)
        elif self.CurrentData == 'text':
            self.text += content
        elif self.CurrentData == 'id' and self.idDoc == 0:
            self.id = content
            self.idDoc = 1
            # print('id:', content)

    def endElement(self, tag):

        if tag == 'page':
            # i = InvertedIndexing()
            # print(self.title)
            # title = i.stem(self.title.lower())
            # i.cleaning(title, self.text, self.id)

            # print(' '.join(title))
            # print(title)
            dataset.append((self.id, self.title, self.text))
            self.title = ''
            self.text = ''
            self.id = ''
            self.CurrentData = ''
            self.idDoc = 0
            # print('Page End')


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

i = InvertedIndexing()
i.cleaning(dataset)


t2 = time.time()

if not os.path.isdir(sys.argv[2]):
    os.mkdir(sys.argv[2])

keys = 0


with open(f'{sys.argv[2]}/index.txt', 'a') as f:

    for w in index:
        keys += 1
        print(w, index[w],  file=f)

f = open(f'{sys.argv[3]}', 'w')
f.write(f'{TOTAL}\n{keys}\n')
f.close()
for i in index.keys():
    print(i, index[i])

print('Time Taken in Seconds:', str(t2-t1))

