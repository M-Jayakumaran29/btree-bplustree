#m_m
"""
main.py

Demonstrates the BTree and BPlusTree classes from btree_bplustree.py
"""

from btree_bplustree import BTree, BPlusTree


def demo_btree():
    print("===== B-TREE DEMO =====")
    tree = BTree(order=4)

    values = [50, 30, 70, 20, 40, 60, 80, 10, 90, 25]
    for v in values:
        tree.insert(v)

    print("Inserted:", values)
    print("Traversal (sorted):", tree.traverse())

    print("Search 40:", tree.search(40))
    print("Search 99:", tree.search(99))

    tree.delete(30)
    tree.delete(90)
    print("After deleting 30 and 90:", tree.traverse())


def demo_bplus_tree():
    print("\n===== B+ TREE DEMO =====")
    tree = BPlusTree(order=4)

    values = [50, 30, 70, 20, 40, 60, 80, 10, 90, 25]
    for v in values:
        tree.insert(v, "item-" + str(v))

    print("Inserted:", values)
    print("Traversal (sorted key-value pairs):", tree.traverse())

    print("Search 40:", tree.search(40))
    print("Search 99:", tree.search(99))

    tree.delete(30)
    tree.delete(90)
    print("After deleting 30 and 90:", tree.traverse())


if __name__ == "__main__":
    demo_btree()
    demo_bplus_tree()
