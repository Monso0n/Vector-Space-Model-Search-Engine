from search2 import SearchEngine

a = SearchEngine() #instantiate search engine

queryFile = open("cacm/query.text", 'r') #import files for reading
relFile = open("cacm/qrels.text", 'r')

mode = None

queries = {}

q = ""
num = None

for i in queryFile: # get queries, put them in dict
    if i.startswith("."):
        mode = i.split()[0]

        if i.startswith(".I"):
            queries[num] = q
            q = ""

            num = int(i.split()[1])

    elif mode == ".W":
        q += i + " "

queries.pop(None)
print("\n")
#print(queries)

relevant = {}

num = 0
for i in relFile: #get relevant files, put them in dict
    num = int(i.split()[0])
    docId = int(i.split()[1])

    #print(f"{num}  {docId}")

    if num not in relevant:
        relevant[num] = [docId]
    elif num in relevant:
        list = relevant[num]
        list.append(docId)

        relevant[num] = list


def MAP(ret, rel): #returns average precision of top 10

    precisionSum = 0
    relevantCount = 0
    position = 0

    for i in ret:
        position+=1

        if i in rel:
            relevantCount+=1

            prec = relevantCount/position
            print(f"'{i}' is at index {position}, precision for retrieved doc is: {prec} = {relevantCount} / {position}")
            precisionSum+=prec


    AP = precisionSum / len(rel)
    print(f"\nThe Average Precision is: {AP} = {precisionSum} / {len(rel)}")
    return AP


def rPrec(ret, rel):

    count = 0
    size = len(rel)


    if len(rel) > len(ret):
        print("OVER HERE")
        for i in rel:
            if i in ret:
                count+=1
    else:
        for i in range(size):
            if ret[i] in rel:
                count+=1


    rprecision = count/size
    print(f"{count} relevant results in top {size} retrieved")
    print("\nThe R-Precision is: {} = {} / {}\n".format(rprecision,count,size))
    return rprecision


rprecisionList = []
APList = []

for k, v in relevant.items():

    query = queries[k]
    print("--------------------------------------------------------------------------------")
    print(f"Query Number: {k}")
    rel = relevant[k]

    returned = a.search(query, False)

    retrieved = []
    for i in returned:
        retrieved.append(i[0])


    print(f"query(shortened): {query[:150]}")
    print("relevant docIDs: {}".format(rel))
    print("retrieved docIDs: {}\n".format(retrieved))

    prec = rPrec(retrieved, rel)
    AP = MAP(retrieved, rel)

    APList.append(AP)
    rprecisionList.append(prec)
    print("\n")


print("\n----------------------------------------------")

print("All queries processed\nAverage Results")
print(f"Average R-Precision: {sum(rprecisionList) / len(rprecisionList)}")
print(f"Mean Average Precision: {sum(APList) / len(APList)}")

