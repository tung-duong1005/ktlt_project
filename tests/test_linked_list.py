"""Tests for MyLinkedList data structure."""

from app.core.linked_list import MyLinkedList


def test_linked_list():
    print("Testing MyLinkedList...")
    lst = MyLinkedList()
    assert lst.size() == 0

    lst.addLast("A")
    lst.addLast("B")
    lst.addLast("C")
    assert lst.size() == 3
    assert lst.get(0) == "A"
    assert lst.get(1) == "B"
    assert lst.get(2) == "C"

    # test find
    found = lst.find(lambda x: x == "B")
    assert found == "B"

    # test remove from middle
    removed = lst.remove("B")
    assert removed is True
    assert lst.size() == 2
    assert lst.get(0) == "A"
    assert lst.get(1) == "C"

    # test remove head
    removed = lst.remove("A")
    assert removed is True
    assert lst.size() == 1
    assert lst.get(0) == "C"
    assert lst.head.data == "C"
    assert lst.tail.data == "C"

    # test remove last
    removed = lst.remove("C")
    assert removed is True
    assert lst.size() == 0
    assert lst.head is None
    assert lst.tail is None
    print("MyLinkedList tests passed!")


def test_split_line():
    print("Testing _split_line (pipe delimiter)...")
    from app.services.attendance_manager import AttendanceManager
    split = AttendanceManager._split_line

    res = split("CS101|Introduction to Programming|A101")
    assert res.size() == 3
    assert res.get(0) == "CS101"
    assert res.get(1) == "Introduction to Programming"
    assert res.get(2) == "A101"
    print("_split_line tests passed!")


if __name__ == "__main__":
    test_linked_list()
    test_split_line()
    print("All linked list tests passed!")
