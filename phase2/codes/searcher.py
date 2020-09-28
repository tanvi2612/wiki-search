import pickle
import Stemmer
import sys
import re
from collections import defaultdict
import numpy as np
import time
ind = {'n': 0, 't': 1, 'b': 2, 'i': 3, 'l': 4, 'r': 5, 'c': 6}
ps = Stemmer.Stemmer('english')

doc_data = {}
tf = []
tf.append(open(f"{sys.argv[1]}/tf.txt", 'r'))
tf.append(open(f"{sys.argv[1]}/tf_1.txt", 'r'))

total_doc = []
total_doc.append(open(f"{sys.argv[1]}/docs.txt", 'r'))
total_doc.append(open(f"{sys.argv[1]}/docs_1.txt", 'r'))
print('reading start')
# idf = open(f"try/idf.txt", 'r')
for i in total_doc:
    lines = i.read().split('\n')
    TOTAL = int(lines[0])
    for l in lines[1:]:
        l = l.split()
        if(len(l) > 1):
            if int(l[0]) > TOTAL:
                TOTAL = int(l[0])  
            doc_data[l[0]] = ' '.join(l[1:])

print('doc reading done')

lines1 = tf[0].readlines()
lines2 = tf[1].readlines()
lines = lines1 + lines2

print('preprocessing done')


tf[0].close()


output_doc = open('queries_op_2.txt​', 'w')

query_doc = open(f"{sys.argv[2]}", 'r')

query = query_doc.readlines()

for q in query:
    print(q)
    tfidf = {}
    q = q.split(',')
    k = int(q[0].strip())
    temp = q[1].split(':')
    words = {}
    if len(temp) == 1:
    	#print('Normal Query')
        stemmed_words = ps.stemWords(temp[0].lower().split())
        words['n']  = {}
        for w in stemmed_words:
            words['n'][w] = {}
    else:

        # words[temp[0]] = []
        flag = temp[0]
        flag = flag.strip()
        for i in temp[1:-1]:

            stemmed_words = ps.stemWords(i[:-1].lower().split())
            # print(flag)

            words[flag] = {}
            for w in stemmed_words:
                words[flag][w.strip()] = {}
            # words[i[-1]] = []
            flag = i[-1].strip()

        stemmed_words = ps.stemWords(temp[len(temp)-1].lower().split())

        words[flag] = {}
        for w in stemmed_words:
            words[flag][w] = {}

    # print(words)
    t_start = time.time()
    standby = words
    for l in lines:
        l = l.split()
        if len(l) > 1:
            sent = [l[0], ''.join(l[1:]).strip('{}').split(';')]
            
            for letter in words.keys():
                # letter = letter.strip()
                for w in words[letter].keys():
                    
                    # w = w.strip()
                    # print( w)
                    if sent[0] == w:
                        di = 0
                        # print(sent)

                        docs = {}
                        for d in sent[1][:-1]:
                            # print(d)
                            d = d.split(':')
                            #print(d)
                            if d[0] == 'total':
                                #print(d[1])
                                di = int(d[1])
                                continue
                            # d[0]  = d.strip()
                            d[1] = ''.join(d[1]).strip('[]').split(',')
                            #print(d[1], ind[letter])
                            #print(d[1][ind[letter]].strip())

                            if d[1][ind[letter]].strip() != '0':
                                wi = int(d[1][ind[letter]].strip())
                                
                                words[letter][w][d[0]] = np.log(
                                    1 + wi) * np.log(TOTAL/di)
                                if d[0] in tfidf.keys():
                                    tfidf[d[0]] += words[letter][w][d[0]]
                                else:
                                    tfidf[d[0]] = words[letter][w][d[0]]

                            else:
                                wi = int(d[1][0].strip())
                               
                                standby[letter][w][d[0]] = - \
                                    np.log(1 + wi) * np.log(TOTAL/di) / 2


    # print('letter searching done')
    for letter in words.keys():
        for w in words[letter].keys():
            if words[letter][w] == {}:
                words[letter][w] = standby[letter][w]
                for d in words[letter][w].keys():
                    if d in tfidf.keys():
                        tfidf[d] += words[letter][w][d]
                    else:
                        tfidf[d] = words[letter][w][d]
    ranking = {}
    ranking = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
    #print(ranking)
    if len(ranking) > 1:
        print('Prining Now')
        
    for r in range(k):
        if r >= len(ranking):
    	    print("No Results Found")
    	    break
        print(ranking[r])
        if ranking[r][0] not in doc_data.keys():
            continue
        print(ranking[r][0], doc_data[ranking[r][0]], file=output_doc)
        print(ranking[r][0], doc_data[ranking[r][0]])
    time_taken = round(time.time() - t_start, 2)
    print(str(time_taken), str(round(time_taken/k, 2)), file=output_doc )
    print('', file=output_doc)
    # print(letter, w, words[letter][w])

output_doc.close()
query_doc.close()
