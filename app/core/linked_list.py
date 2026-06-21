class Node:
    """A node in a singly linked list.

    Attributes:
        data: The payload data stored in the node.
        next (Node): Reference to the next node in the list, or None.
    """

    def __init__(self, data=None):
        """Initializes the Node with data and a null next pointer."""
        self.data = data
        self.next = None


class MyLinkedList:
    """A custom singly linked list implementation.

    Attributes:
        head (Node): The first node in the list.
        tail (Node): The last node in the list.
        _size (int): The number of elements in the list.
    """

    def __init__(self):
        """Initializes an empty linked list."""
        self.head = None
        self.tail = None
        self._size = 0

    def addLast(self, item):
        """Appends an item to the end of the list in O(1) time.

        Args:
            item: The data item to append to the list.
        """
        new_node = Node(item)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def remove(self, item) -> bool:
        """Removes the first node whose data matches the specified item.

        Args:
            item: The value to match, or a predicate function returning bool.

        Returns:
            bool: True if the item was found and successfully removed, False otherwise.
        """
        if self.head is None:
            return False

        # Helper to determine match
        def is_match(data):
            if callable(item):
                return item(data)
            return data == item

        # Check head node
        if is_match(self.head.data):
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self._size -= 1
            return True

        # Check subsequent nodes
        prev = self.head
        curr = self.head.next
        while curr is not None:
            if is_match(curr.data):
                prev.next = curr.next
                if curr == self.tail:
                    self.tail = prev
                self._size -= 1
                return True
            prev = curr
            curr = curr.next

        return False

    def find(self, condition):
        """Finds the first item that satisfies the predicate condition.

        Args:
            condition (callable): A function that takes an item and returns bool.

        Returns:
            The first matching item data, or None if no match is found.
        """
        curr = self.head
        while curr is not None:
            if condition(curr.data):
                return curr.data
            curr = curr.next
        return None

    def traverse(self, action):
        """Performs a linear scan, calling the action function for each element.

        Args:
            action (callable): A function to invoke with each node's data.
        """
        curr = self.head
        while curr is not None:
            action(curr.data)
            curr = curr.next

    def size(self) -> int:
        """Returns the pre-tracked size of the list in O(1) time.

        Returns:
            int: The number of elements in the list.
        """
        return self._size

    def get(self, index: int):
        """Retrieves the item data at the specified index.

        Args:
            index (int): The 0-based index of the item.

        Returns:
            The item data at the index, or None if the index is out of bounds.
        """
        if index < 0 or index >= self._size:
            return None
        curr = self.head
        count = 0
        while curr is not None:
            if count == index:
                return curr.data
            curr = curr.next
            count += 1
        return None
