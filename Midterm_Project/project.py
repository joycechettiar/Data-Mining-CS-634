import sys
import time


filename=sys.argv[1]                            #The first argument is the filename
min_support=float(sys.argv[2])                  #The second argument is the minimum support
min_confidence =float(sys.argv[3])              #The third argument is the minimum confidence



with open("all_items.csv") as f:
    Brute_items = f.read().replace("\n", "").split(",")
    Brute_items.sort()
    

filedata=open(filename,"r")
data=filedata.readlines()
data=[l.replace("\n","").split(",") for l in data]
print("-----------------------------------------------------")
print("             INPUT DATA")
print("-----------------------------------------------------")
for t in data:
    print(t)

    
class Brute:

    def __init__(self,Brute_left,Brute_right,Brute_all):
        self.Brute_left = list(Brute_left)
        self.Brute_left.sort()
        self.Brute_right = list(Brute_right)
        self.Brute_right.sort()
        self.Brute_all =Brute_all

    def __str__(self):
        return ",".join(self.Brute_left)+" => "+",".join(self.Brute_right)


def Brute_generate_k(items, k):

    if k == 1:
        return [[x] for x in items]

    all_res = []
    for i in range(len(items)-(k-1)):
        for sub in Brute_generate_k(items[i+1:], k-1):
            tmp = [items[i]]
            tmp.extend(sub)
            all_res.append(tmp)
    return all_res


def Brute_scan(db, s):
    count = 0
    for t in db:
        if set(s).issubset(t):
            count += 1
    return count
    
    
print("-----------------------------------------------------")
print("             Start of Brute force")
print("-----------------------------------------------------")
B_start_time = time.time()
B_frequent = []
B_support = {}

for k in range(1, len(Brute_items)+1):
    B_current = []
    for comb in Brute_generate_k(Brute_items, k):
        count = Brute_scan(data, comb)
        if count/len(data) >= min_support:
            B_support[frozenset(comb)] = count/len(data)
            B_current.append(comb)
    if len(B_current) == 0:
        break
    B_frequent.append(B_current)

all_rule = set()
Brute_all_result = []
for k_freq in B_frequent:
    if len(k_freq) == 0:
        continue
    if len(k_freq[0]) < 2:
        continue
    for freq in k_freq:
        for i in range(1, len(freq)):
            for left in Brute_generate_k(freq, i):
                tmp = freq.copy()
                right = [x for x in tmp if x not in left]
                all_rule.add(Brute(left, right, freq))
for rule in all_rule:
    Brute_confidence = B_support[frozenset(rule.Brute_all)] / B_support[frozenset(rule.Brute_left)]
    if Brute_confidence >= min_confidence:
        Brute_all_result.append([rule, B_support[frozenset(rule.Brute_all)], Brute_confidence])

Brute_all_result.sort(key=lambda x: str(x[0]))
B_end_time = time.time()
print("-----------------------------------------------------")
print("                RULES SUPPORT CONFIDENCE:")
print("-----------------------------------------------------")
for r in Brute_all_result:
    print(r[0], r[1], r[2])
print("-----------------------------------------------------")
print("                RUNNING TIME FOR BRUTE FORCE")
print("-----------------------------------------------------")
print(str(B_end_time - B_start_time) + "s")



class Apriori:
    def __init__(self,Apriori_left,apriori_right,apriori_all):
        self.Apriori_left=list(Apriori_left)
        self.Apriori_left.sort()
        self.apriori_right=list(apriori_right)
        self.apriori_right.sort()
        self.apriori_all=apriori_all

    def __str__(self):
        return ",".join(self.Apriori_left)+" => "+",".join(self.apriori_right)


def Apriori_generating_sub_rule(fs,r,result,support):
    r_size=len(r[0])
    t_size=len(fs)
    if t_size-r_size>0:
        r=Apriori_generate_items(r)
        new_r=[]
        for i in r:
            l=fs-i
            if(len(l)==0):
                continue
            confidence=support[fs]/support[l]
            if(confidence>=min_confidence):
                result.append([Apriori(l,i,fs),support[fs],confidence])
                new_r.append(i)

        if(len(new_r)>1):
            Apriori_generating_sub_rule(fs,new_r,result,support)


def Apriori_generate_items(dk):
    res=[]
    for i in range(len(dk)):
        for j in range(i+1,len(dk)):
            l,r=dk[i],dk[j]
            ll,rr=list(l),list(r)
            ll.sort()
            rr.sort()
            if ll[:len(l)-1] == rr[:len(r)-1]:
                res.append(l | r)
    return res


def Apriori_scan(data,f1):
    count = {s:0 for s in f1}
    for i in data:
        for freqset in f1:
            if(freqset.issubset(i)):
                count[freqset]+=1
    n=len(data)
    return{freqset: support/n for freqset, support in count.items() if support/n>=min_support}
    
   

#Start for Apriori alogorithm
print("-----------------------------------------------------")
print("                Start of Apriori")
print("-----------------------------------------------------")
start_time = time.time()
support={}
item=[[]]
dk=[[]]
f1=set() #creating a set to hold all the data for scanning the data from the dictionary
for i in data:
    for items in i:
        f1.add(frozenset([items]))
item.append(f1)
count=Apriori_scan(data,f1)
dk.append(list(count.keys()))
support.update(count)

t=1
while len(dk[t]) > 0:
    item.append(Apriori_generate_items(dk[t]))
    count=Apriori_scan(data,item[t+1])
    support.update(count)
    dk.append(list(count.keys()))
    t+=1
#generation of the rules

result=[]

for i in range(2,len(dk)):
    if(len(dk[i])==0):
        break
    frequent_set=dk[i]

    for fs in frequent_set:
        for r in [frozenset([x]) for x in fs]:
            l=fs-r
            confidence=support[fs]/support[l]
            if confidence>=min_confidence:
                result.append([Apriori(l,r,fs),support[fs],confidence])
    if(len(frequent_set[0])!=2):
        for fs in frequent_set:
            r=[frozenset([x]) for x in fs]
            Apriori_generating_sub_rule(fs,r,result,support)

result.sort(key=lambda x: str(x[0]))
end_time=time.time()

for k in result:
    print(k[0],k[1],k[2])
print("-----------------------------------------------------")
print("                  RUNNING TIME FOR APRIORI")
print("-----------------------------------------------------")
print(str(end_time - start_time) + "s")



