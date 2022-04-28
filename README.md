# 507-final-project
## DATA STRUCTURE  
The basic B-Tree data structure is implemented in the btree.py file, which is often
used to implement databases because of its good query performance, especially
on traditional mechanical disks; this is because for B-Trees , each node is an ordered
list, the data of this list will be stored on the disk in blocks, and for traditional
mechanical disks, this will reduce the total seek time of the target data.
When querying the target data, it will first start from the root node to check whether
the target data is in this node; when the target data is not queried, it will extend
downward until it reaches the leaf node.  
The time complexity of the query is:
Iteration: O(logm n)  
Compare:O(log2m * logmn)    
Here, because the data within each node is ordered, binary search optimization
can be used.
 ...  
class Comparable(Protocol):
"""Protocol for annotating comparable types."""  
@abstractmethod  
def __lt__(self: 'CT', other: 'CT', /) -> bool:  
 ...
CT = TypeVar('CT', bound=Comparable)  
ST = TypeVar('ST', bound=Serializable)  
When persistent storage is required, the dump function of the root node of the B-Tree
can be called, which will recursively call the dump function of the child nodes and
return a dictionary; due to the use of type hints, the data element class implements
own dump function, so the dictionary can be saved as a file using the json library.
When the tree needs to be loaded, the recursive function is also used to build the
leaf nodes from top to bottom.
## MOVIE CLASS ABSTRACT

The abstraction of the movie class is implemented in the movies.py file, and
redundant code is reduced by decorating the movie class with
dataclasses.dataclass

Meanwhile, the Movie class inherits the Serializable interface, which means that
it can be indexed directly in the B-Tree by implementing the dump & load
methods.

## CRAWLER  

In scrawler.py , with the help of request and beautifulsoup libraries, we
implement a simple web crawler, which can directly obtain data from IMDb web
pages. The reason for this is that most of IMDb's APIs need to be charged, and the
price is not high. Philip.  
The data captured here is: the top 1000 movie data in the IMDb database. 

## ANALYZE DATA

Using matplotlib , we performed a simple analysis of the captured data. The
analysis items are:  
Top 5 movie actors - by total votes  
5 most popular movies - by total votes  
Number of movies released each year  
Total audience votes per year  
Proportion of different movie categories  
