
import bisect
from dataclasses import dataclass
from abc import abstractmethod, abstractclassmethod
from typing import Any, Dict, Generic, Iterator, List, Optional, Type, TypeVar, Protocol, Union


class Serializable(Protocol):
    """Protocol for serializable data types."""

    @abstractmethod
    def dump(self) -> Any:
        ...

    @abstractclassmethod
    def load(cls: Type['ST'], data: Any) -> 'ST':
        ...


class Comparable(Protocol):
    """Protocol for annotating comparable types."""

    @abstractmethod
    def __lt__(self: 'CT', other: 'CT', /) -> bool:
        ...


CT = TypeVar('CT', bound=Comparable)
ST = TypeVar('ST', bound=Serializable)


@dataclass
class Indexer(Generic[CT, ST]):
    """Indexer for BNode."""

    index: CT
    data: Optional[ST]

    def __lt__(self, other: 'Indexer[CT, ST]') -> bool:
        return self.index < other.index

    def __eq__(self, other: 'Indexer[CT, ST]') -> bool:
        return self.index == other.index

    def dump(self) -> Dict:
        data = self.data.dump() if self.data else None
        return {
            'index': self.index,
            'data': data
        }

    @classmethod
    def load(cls, dumped: Dict):
        return cls(dumped['index'], dumped['data'])


class BNode(Generic[CT, ST]):
    """BNode is node of BTree, which stores bucket data.

    Args:
        size (int): bucket size.
        father (Optional[BNode], optional): father node. Defaults to None.    

    Raises:
        ValueError: once bucket size is not ``2n+1``.
    """

    def __init__(self, maxsize: int, father: Optional['BNode[CT, ST]'] = None) -> None:
        if not (maxsize > 2 and maxsize % 2 == 1):
            raise ValueError(f'invalid BNode bucket size {maxsize}')
        self._maxsize = maxsize
        self._bucket: List[Indexer[CT, ST]] = list()
        self._children: List['BNode[CT, ST]'] = []
        self._father = father

    @property
    def isleaf(self) -> bool:
        return not self._children

    @property
    def children(self) -> Iterator['BNode[CT, ST]']:
        return iter(self._children)

    @property
    def father(self) -> Optional['BNode[CT, ST]']:
        return self._father

    def add(self, indexer: Indexer) -> None:
        """Add a element to this node, this node must be a leaf node:

        Procedure:

        - if this node is a leaf node, simply add this element to bucket,
        - check if current node need to be splited.

        Note: this function will not add element if current node is not leaf node.
        """
        if not self.isleaf:
            raise ValueError('adding indexer to a non-leaf node')
        if indexer in self:
            raise ValueError('indexer found')
        bisect.insort(self._bucket, indexer)
        if len(self._bucket) == self._maxsize:
            self._split()

    def _add_with_subnodes(self, indexer: Indexer[CT, ST], right: 'BNode[CT, ST]') -> None:
        """Add with subnodes.

        After adding, it will check if need to split again.

        Note: this method should not be called by other function except ``self._split``.
        """
        index = bisect.bisect(self._bucket, indexer)
        self._bucket.insert(index, indexer)
        self._children.insert(index + 1, right)
        right._father = self
        if len(self._bucket) == self._maxsize:
            self._split()

    def __iter__(self) -> Iterator[Indexer[CT, ST]]:
        """Iter all elements in bucket."""
        return iter(self._bucket)

    def exist(self, indexer: Indexer[CT, ST]) -> bool:
        """Check indexer in ``self._bucket``."""
        index = bisect.bisect_left(self._bucket, indexer)
        if index >= len(self._bucket):
            return False
        return self._bucket[index] == indexer

    def subindex(self, indexer: Indexer[CT, ST]) -> 'BNode':
        """Return subnode with given index."""
        if self.isleaf:
            raise ValueError('indexer not exist')
        return self._children[bisect.bisect(self._bucket, indexer)]

    def _split(self) -> None:
        """Split this node.

        Procedure:

        - split current node into three parts: (BNode(left), center, BNode(right)),
          change current node to left node.
        - if father node is not ``None``:
          call: ``self._father._add_with_subnodes(center, right)``.
        - if father node is ``None``, create an father node, and add this node to father,
          then call ``self._father._add_with_subnodes(center, right)``.

        Note: this method should not be called by other function except ``self.add``.
        """
        assert len(self._bucket) == self._maxsize
        cursor = self._maxsize // 2

        # Get center element
        center = self._bucket[cursor]

        # Create right subnode for father
        right = BNode(self._maxsize)
        right._bucket = self._bucket[cursor + 1:]
        right._children = self._children[cursor + 1:]

        # Set current node to left node
        self._bucket = self._bucket[:cursor]
        self._children = self._children[:cursor + 1]

        # Reset children
        for child in right.children:
            child._father = right

        # Add to father node
        if self._father is None:
            self._father = BNode(self._maxsize)
            self._father._bucket.append(center)
            self._father._children = [self, right]
            right._father = self._father
        else:
            self._father._add_with_subnodes(center, right)

    def dump(self) -> Dict[str, Any]:
        """Dump current node and subnodes recursively.

        It will save data using like:

        ```json
        {
            "elements": self._bucket,
            "children": [ ... ],
            "maxsize": self._size
        }
        ```

        Return a dict for dump to JSON
        """
        dumped = {
            'indexs': [],
            'children': [],
            'maxsize': self._maxsize
        }
        for indexer in self._bucket:
            dumped['indexs'].append(indexer.dump())
        for child in self._children:
            dumped['children'].append(child.dump())
        return dumped

    @classmethod
    def load(cls, dumped: Dict[str, Any]) -> 'BNode[CT, ST]':
        """Load data from dumped dict.

        Data format written above, see ``self.dump`` funciton.
        """
        current = cls(dumped['maxsize'])
        for indexer in dumped['indexs']:
            current._bucket.append(Indexer.load(indexer))
        for child in dumped['children']:
            current._children.append(BNode.load(child))
        return current


class BTree(Generic[CT, ST]):

    BucketSize = 5

    def __init__(self, maxsize: int = BucketSize) -> None:
        self._root: BNode[CT, ST] = BNode(maxsize, father=None)

    def insert(self, index: CT, data: ST) -> None:
        """Insert element to BTree.

        Procedure:

        - Iterate until find leaf node, index with given element.

        Args:
            element (CT): element want to add to tree.
        """
        current, indexer = self._root, Indexer(index, data)
        while not current.isleaf:
            current = current.subindex(indexer)
        current.add(indexer)

        # Check if current is still root
        while self._root.father:
            self._root = self._root.father

    def find(self, index: CT) -> Optional[ST]:
        """Find by index."""
        current, target = self._root, Indexer(index, data=None)
        while not current.isleaf:
            if current.exist(target):
                break
            current = current.subindex(target)
        for indexer in current:
            if indexer.index == index:
                return indexer.data
        raise ValueError(f'index {index} not in tree')

    def dump(self) -> Dict:
        return self._root.dump()

    @classmethod
    def load(cls, data: Dict):
        tree = cls()
        tree._root = BNode.load(data)  # type: ignore
        return tree

    def __len__(self) -> int:
        """Using BFS for counting total index number."""
        unvisited: List[BNode[CT, ST]] = [self._root]
        count: int = 0
        while unvisited:
            current = unvisited.pop()
            count += len(list(current))
            unvisited.extend(current.children)
        return count


if __name__ == '__main__':

    class IntWrapper(Serializable):

        def __init__(self, data: int) -> None:
            self._data = data

        def dump(self) -> int:
            return self._data

        @classmethod
        def load(cls, data: int):
            return cls(data)

    tree: BTree[int, IntWrapper] = BTree()
    for index in (39, 22, 97, 41, 53, 13, 21, 40, 30, 27, 33, 36, 35, 34, 24, 29, 26, 17, 28, 23, 31, 32):
        tree.insert(index, IntWrapper(index))

    import json
    dumps = json.dumps(tree.dump(), indent=4)
    tree: BTree[int, IntWrapper] = BTree.load(json.loads(dumps))
    assert tree.find(39) == 39  # type: ignore
