# Vector-Space-Information-Engine
A search engine built utilizing the Vector Space model for information retrieval.  

This application analyzes the documents in the cacm.all file and builds the inverted index using invert2.py. After the index is built, search2.py builds the document vectors for information analysis. Free-text queries can be inputted for a result. Top-K retrieval using document-at-a-time calculation is used to display the top-10 relevant documents. The K value can be changed. Word stemming and stop-word removal can be enabled or disabled.

# TO RUN
1. ensure all files are  in the same directory.
2. run search2.py.
3. input whether word stemming and stop-word removal should be used.
4. input free text queries

## eval.py

A Program to analyze the performance of the search engine. Using query.text for query and qrels.text for relavent document set.

For each query the program displays the R-Precision and Average precision of each entry. The program displays the Measured Average Precision (MAP) and average R-Precision at the end.

