from PorterStemmer import PorterStemmer
from collections import Counter
import math
import invert2

class SearchEngine:
    def __init__(self):
        while True:
            x = input("Do you want to enable stemming? (y/n): ")
            x = x.lower()

            if x == "y":
                self.STEMMER_ENABLED = True
                print("Input accepted.")
                break
            elif x == "n":
                self.STEMMER_ENABLED = False
                print("Input accepted")
                break
            else:
                print("Invalid entry")

        while True:
            x = input("Do you want to enable stop word removal? (y/n): ")
            x = x.lower()

            if x == "y":
                self.SW_ENABLED = True
                print("Input accepted")
                break
            elif x == "n":
                self.SW_ENABLED = False
                print("Input accepted")
                break
            else:
                print("Invalid entry")

        invert2.run(self.SW_ENABLED, self.STEMMER_ENABLED)

        self.dict = open("dictionary.txt").read() #open dictionary and postings file to read from
        self.postings = open("postings.txt").read()
        self.docs = open("documents.txt", 'r').read().splitlines()


        self.sw = open("cacm/common_words", 'r')
        self.p = PorterStemmer()

        self.stopwords = self.sw.read().split()
        self.NUMBER_OF_DOCUMENTS = 3203

        self.wordIndex = {}
        self.vocabulary = [[]] #vocabulary contains the terms with respective docFreq


        print("\nRunning Constructor")

        count = 0
        print("Adding Terms and Document Frequency to Vocabulary")
        for line in self.dict.splitlines(): #append term and docFreq to vocabulary
            t = []
            count+=1

            word = line.split()[0]

            t.append(word)
            t.append(int(line.split()[1].replace('[', '').replace(']', '')))

            self.wordIndex[word] = count
            #print(t)

            self.vocabulary.append(t)
        print("Vocabulary built")
        print(f"Number of terms in vocabulary is : {len(self.vocabulary)}")


        def fillMatrix():
            self.weightMatrix = [[0 for x in range(len(self.vocabulary)+2)] for y in range(self.NUMBER_OF_DOCUMENTS + 1)]

            termNum = 0

            print("Building Matrix")
            for i in self.vocabulary:
                #print(f"{i} is in weightMatrix[0][{termNum}]")   #put the term on the top
                self.weightMatrix[0][termNum] = i
                #if termNum>1: print(self.weightMatrix[0][termNum][1])
                termNum += 1

            for i in range(self.NUMBER_OF_DOCUMENTS):
                self.weightMatrix[i+1][0]=f"Document {i+1} " #put document ID

            print("Adding Titles Complete")

            termNum = 0


            for line in self.postings.splitlines():
                line = line.replace('(', '').replace(')', '')
                line = line.split(', ')

                termNum+=1

                IDF = math.log(self.NUMBER_OF_DOCUMENTS / self.weightMatrix[0][termNum][1])
                #print(f"IDF of {self.weightMatrix[0][termNum][0]} is: log({self.NUMBER_OF_DOCUMENTS}/{self.weightMatrix[0][termNum][1]}) = {IDF}")

                #print(line)
                for entry in line:
                    doc = int(entry.split(',')[0])
                    termFreq = int(entry.split(',')[1])

                    #print(f"TF is {1+math.log(termFreq, 10)}  IDF is {IDF}  Weight = {(1 + math.log(termFreq,10))*IDF}")
                    if termFreq == 0:
                        self.weightMatrix[doc][termNum] = 0
                    else:
                        self.weightMatrix[doc][termNum] = ((1 + math.log(termFreq, 10)) * IDF)

            print("Weight Vectors have been added")

            for i in self.weightMatrix[1:]:
                norm = i[1:-1]
                weight = 0
                for e in norm:
                    if e != 0:
                        weight += e**2

                i[-1]=math.sqrt(weight)
                #print(f"{i[0]} weight: {i[-1]}")
            print("Finished calculating Norm of Document Vectors")

        fillMatrix()

        print("Finished building matrix")


        #[docNumber][termID]
        #[row][col]
        #print(self.weightMatrix[1631][3283])
        #print(self.weightMatrix[0][3283])
        #print(self.weightMatrix[1631][0])
        #print(self.weightMatrix[1631][-1])


    def getIDF(self, word):
        index = self.getIndex(word)
        if index!=-1:
            frequency = self.vocabulary[index][1]
            #print(f"frequency of {word} is {frequency}, IDF is {math.log(self.NUMBER_OF_DOCUMENTS/frequency,10)}")
            return math.log(self.NUMBER_OF_DOCUMENTS/frequency, 10)
        else:
            return -1


    def getNorm(self, documentID):
        return self.weightMatrix[documentID][-1]

    def getIndex(self, word):
        if word in self.wordIndex:
            #print(f"{word} is on line {self.wordIndex[word]}")
            return self.wordIndex[word]
        else:
            #print(f"'{word}' not in index")
            return -1

            
    def process(self, string):
        processedQuery = ""
        punctuation = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''

        string = string.lower()

        for char in string:
            if char in punctuation:
                string = string.replace(char, ' ')

        if self.SW_ENABLED:
            for w in string.split():
                if w in self.stopwords:
                    continue
                else:
                    processedQuery += f"{w} "
        else:
            processedQuery = string

        if self.STEMMER_ENABLED:
            query = processedQuery.split()
            
            processedQuery = ""

            for w in query:
                processedQuery += self.p.stem(w, 0, len(w)-1) + " "

        #print("processed query:")
        #print(processedQuery)
        return processedQuery

    def findScores(self, qweight, docNumber, norm):
        top = 0
        for word in qweight:
            index = self.getIndex(word)
            weight = self.weightMatrix[docNumber][index]
            top += weight * qweight[word]

        if (norm * self.weightMatrix[docNumber][-1]) == 0:
            return None

        score = top / (norm * self.weightMatrix[docNumber][-1])
        if score != 0:
            #print(f"doc {docNumber} score is {top}/{(norm * self.weightMatrix[docNumber][-1])} = {score}")
            return (docNumber, score)
        else:
            return None

    def search(self, query, post):
        OGQuery = query
        processedQuery = self.process(query)
        processedQuery = processedQuery.split()

        processedQuery = sorted(processedQuery)

        qWeight = Counter(processedQuery)
        #print(dict(qWeight))

        norm = 0

        removeWords = []

        for word in qWeight:
          freq = qWeight[word]
          IDF = self.getIDF(word)
          if IDF == -1:
              removeWords.append(word)
              #print(f"removed {word}")
          else:
              #print(f"IDF of {word} is {self.getIDF(word)}")
              weight = (1 + math.log(freq, 10))*self.getIDF(word)
              qWeight[word] = weight

              norm += weight**2

        for i in removeWords:
            qWeight.pop(i)

        norm = math.sqrt(norm)

        #print(dict(qWeight))
        #print(f"the length of the query vector is: {norm}")

        processedQuery = list(qWeight.keys())
        #print(f" new query: {processedQuery}")

        topK = []

        for i in range(1, self.NUMBER_OF_DOCUMENTS):
            score = self.findScores(qWeight, i, norm)
            if score is not None:
                topK.append(score)

        topK = sorted(topK, key = lambda x: x[1], reverse=True)
        K= 10


        if len(topK) > K:
            toReturn = topK[0: K]
        else:
            toReturn = topK
        #print(topK)

        if post:
            self.printTopK(toReturn, OGQuery)
        else:
            return topK

        print("\n")

    def printInfo(self, docID):

        docID = str(docID)

        index = self.docs.index(docID) + 1

        title = ""
        authors = ""
        date = ""


        #print(f"{docID} starts at line {index + 1}")
        #Get the title
        if self.docs[index].startswith("   "):
            title = self.docs[index][3:]
            for i in self.docs[index+1:]:
                if i.startswith("   "):
                    break
        else:
            title = self.docs[index]

        print(f"Title: {title}")

        #Get date
        for i in self.docs[index:]:
            if i.startswith("CACM"):
                date = i[5:]
                break

        print(f"Date: {date}")

        #Get Authors
        getAuth = False
        for i in self.docs[index:]:
            if getAuth:
                if len(i) == 0:
                    break
                authors += i + ", "

            if i.startswith("CACM"):
                getAuth = True

        authors = authors[:-2]

        print(f"Author(s): {authors}")


    def printTopK(self, topK, OGQuery):

        if len(topK) == 0:
            print("\nThere are no results for {OGQuery} (terms do not exist in index)")
        else:
            print(f"\nThe Top {len(topK)} Results for query '{OGQuery}' are:")
            ct = 0
            for i in topK:
                ct += 1
                percentMatch = "{:.2%}".format(i[1])
                print(f"{ct}. Document ID: {i[0]} \t\t Percent Match: {percentMatch}")
                self.printInfo(i[0])
                print("\n")


if __name__ == "__main__":
    a = SearchEngine()

    #a.printInfo(1)
    #a.printInfo(2)
    #a.printInfo(3200)

    print("\n")
    while True:
        word = input("Enter a Query: ")
        a.search(word, True)