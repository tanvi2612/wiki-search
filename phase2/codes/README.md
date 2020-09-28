## Code Specifications
---

There are two files for indexing and searching respectively:

For indexing, the file is called indexer.py. To run this file you will have to run

``` python idexer.py $1 $2 $3 ```


here $1 = The address to the dump file (.xml) , $2 is the location where the indexed files should be stroe, $3 is the name of the file that contains the stats. 

The code will output on the terminal 2 lines:\
1. The number of files in the dump
2. The total time taken to reate the index

In addition to this the code will also output 2 files in the $2 location 
1. **tf.txt** containing the frequencies of different words in different documents along with the total number of documents containg those words.
2. **docs.txt** contatins a list of all the document ids and document titles present in the dump

For searching, the file is called searcher.py. To run this file you will have to run

``` python searcher.py $1 $2 ```

Here $1 = The location of the index , $2 is the document containg different queries

The code will output 1 file which will contain the query results. 

     



