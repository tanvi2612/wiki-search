import pickle 
import Stemmer
import sys
import re
from collections import defaultdict

ps = Stemmer.Stemmer('english')
dict_index = {}



if __name__ == "__main__":


    index = open(f"{sys.argv[1]}/index.txt", 'r')
    lines = index.read().split('\n')
    for l in lines: 
        if l != '': 
            
            post = re.split(r'\W+', l) 
            
            dict_index[post[0]] = {}
            tot = len(post)
            for i in range(1,tot):
                if post[i] == '':
                    pass 
                else:
                    temp = post[i]
                    if re.match(r'^d', temp):
                        dict_index[post[0]][temp] = {}
                        cont = i
                        for j in range(i+1, tot):
                            if re.match(r'^[tbclri]$', post[j]):
                                dict_index[post[0]][temp][post[j]] = post[j+1]
                                j = j + 1
                            if re.match(r'^d', post[j]):
                                cont = j-1
                                break 

    
            


             
    
             
    index.close() 
    query = sys.argv[2].split(':')
    # print(query)
    if len(query) == 1:
        words = query[0].split(' ')
        ret = []
        for w in words:
            word = ps.stemWord(w)
            if word in dict_index.keys():
                if not ret:
                    ret = dict_index[word].keys()
                else:
                    ret = set(ret).intersection(dict_index[word].keys()) 
            else:
                print('Word Not found')   
                sys.exit(0)

        for k in ret:
            print(k, dict_index[word][k])

    else:
        for i in range(0, len(query), 2):
            words = query[i+1].split(' ')
            ret = []
            for w in words:
                word = ps.stemWord(w)
                # print(word)
                if word in dict_index.keys():
                    
                    if not ret:
                        print('yes')        
                        for docs in dict_index[word].keys():
                            if query[i] in dict_index[word][docs].keys(): 
                                ret.append(docs)
                    else:
                        temp = []
                        for docs in dict_index[word].keys():
                            if query[i] in dict_index[word][docs].keys(): 
                                temp.append(docs)
                        ret = set(ret).intersection(temp) 
                else:
                    print('Word Not found')   
                    sys.exit(0)

        for k in ret:
            print(k, dict_index[word][k])


    