#m_m
"""
btree_bplustree.py

A small library with two data structures:
    1. BTree      - a balanced search tree (keys stored in every node)
    2. BPlusTree  - a balanced search tree (real data stored only in leaves,
                    leaves linked together for fast sorted traversal)

Both support: search, insert, delete, traverse (sorted order).
"""


# =======================================================
#                       B - T R E E
# =======================================================

class BTreeNode:
    def __init__(self, is_leaf=True):
        self.keys = []
        self.children = []
        self.is_leaf = is_leaf


class BTree:
    def __init__(self, order):
        # order = maximum number of children a node can have
        # max keys in a node = order - 1
        # min keys in a node (except root) = ceil(order / 2) - 1
        self.order = order
        self.max_keys = order - 1
        self.min_keys = (order + 1) // 2 - 1
        self.root = BTreeNode(is_leaf=True)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i = i + 1

        if i < len(node.keys) and node.keys[i] == key:
            return True

        if node.is_leaf:
            return False

        return self._search(node.children[i], key)

    def insert(self, key):
        overflow = self._insert(self.root, key)

        # if the root itself overflowed, make a new root above it
        if overflow is not None:
            middle_key, right_node = overflow
            new_root = BTreeNode(is_leaf=False)
            new_root.keys = [middle_key]
            new_root.children = [self.root, right_node]
            self.root = new_root

    def _insert(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i = i + 1

        if node.is_leaf:
            node.keys.insert(i, key)
        else:
            overflow = self._insert(node.children[i], key)
            if overflow is not None:
                middle_key, right_node = overflow
                node.keys.insert(i, middle_key)
                node.children.insert(i + 1, right_node)

        # too many keys now, split this node and push the middle key up
        if len(node.keys) > self.max_keys:
            return self._split(node)
        return None

    def _split(self, node):
        middle = len(node.keys) // 2
        middle_key = node.keys[middle]

        right_node = BTreeNode(is_leaf=node.is_leaf)
        right_node.keys = node.keys[middle + 1:]
        node.keys = node.keys[:middle]

        if not node.is_leaf:
            right_node.children = node.children[middle + 1:]
            node.children = node.children[:middle + 1]

        return (middle_key, right_node)

    def delete(self, key):
        if not self.search(key):
            print("Key", key, "not found")
            return

        self._delete(self.root, key)

        # if the root became empty, drop one level of height
        if len(self.root.keys) == 0 and not self.root.is_leaf:
            self.root = self.root.children[0]

    def _delete(self, node, key):
        # find the first position i where keys[i] is not smaller than key
        i = 0
        while i < len(node.keys) and node.keys[i] < key:
            i = i + 1

        # case 1: the key is sitting in this node
        if i < len(node.keys) and node.keys[i] == key:
            # if this node is a leaf, just remove the key and we are done
            if node.is_leaf:
                node.keys.pop(i)
                return
            # internal node: take the biggest key of the left subtree (the
            # predecessor); it is the closest smaller key, so order stays valid
            replacement = self._largest_key(node.children[i])
            # put that predecessor in the place of the key we want to delete
            node.keys[i] = replacement
            # now delete the predecessor from the left child, where it came from
            self._delete(node.children[i], replacement)
        # case 2: the key is not in this node, so it can only be in child i
        else:
            # a leaf has no children, so the key is not in the tree at all
            if node.is_leaf:
                return  # key is not in the tree
            # go down into the child that could hold the key
            self._delete(node.children[i], key)

        # we fix the child only AFTER the delete came back up, because only
        # now we know for sure whether that child really lost a key
        # (if we fixed it before, a merge could make a node too big)
        if len(node.children[i].keys) < self.min_keys:
            # the child has too few keys, so borrow from a sibling or merge
            self._fix_shortage(node, i)

    def _largest_key(self, node):
        while not node.is_leaf:
            node = node.children[-1]
        return node.keys[-1]

    def _smallest_key(self, node):
        while not node.is_leaf:
            node = node.children[0]
        return node.keys[0]

    def _fix_shortage(self, node, i):
        has_left_sibling = i > 0
        has_right_sibling = i < len(node.children) - 1

        if has_left_sibling and len(node.children[i - 1].keys) > self.min_keys:
            self._borrow_from_left(node, i)
        elif has_right_sibling and len(node.children[i + 1].keys) > self.min_keys:
            self._borrow_from_right(node, i)
        elif has_right_sibling:
            self._merge(node, i)
        else:
            self._merge(node, i - 1)

    def _borrow_from_left(self, node, i):
        child = node.children[i]
        left_sibling = node.children[i - 1]

        child.keys.insert(0, node.keys[i - 1])
        if not child.is_leaf:
            child.children.insert(0, left_sibling.children.pop())
        node.keys[i - 1] = left_sibling.keys.pop()

    def _borrow_from_right(self, node, i):
        child = node.children[i]
        right_sibling = node.children[i + 1]

        child.keys.append(node.keys[i])
        if not child.is_leaf:
            child.children.append(right_sibling.children.pop(0))
        node.keys[i] = right_sibling.keys.pop(0)

    def _merge(self, node, i):
        left_child = node.children[i]
        right_child = node.children[i + 1]

        left_child.keys.append(node.keys[i])
        left_child.keys.extend(right_child.keys)
        if not left_child.is_leaf:
            left_child.children.extend(right_child.children)

        node.keys.pop(i)
        node.children.pop(i + 1)

    def traverse(self):
        result = []
        self._traverse(self.root, result)
        return result

    def _traverse(self, node, result):
        for i in range(len(node.keys)):
            if not node.is_leaf:
                self._traverse(node.children[i], result)
            result.append(node.keys[i])

        if not node.is_leaf:
            self._traverse(node.children[len(node.keys)], result)


# =======================================================
#                     B + - T R E E
# =======================================================

class BPlusNode:
    def __init__(self, is_leaf=True):
        self.is_leaf = is_leaf
        self.keys = []
        # leaf node   -> children[i] is the VALUE stored for keys[i]
        # internal node -> children[i] is a pointer to a child node
        self.children = []
        self.next_leaf = None  # only used by leaf nodes


class BPlusTree:
    def __init__(self, order):
        self.order = order
        self.max_keys = order - 1
        # a LEAF must keep at least this many keys (this line was already here)
        self.min_keys = order // 2  # minimum keys in a LEAF
        # an INTERNAL node needs a smaller minimum, because when two internal
        # nodes merge, the separator key also comes down into the merged node,
        # so with the bigger number the merged node could get too many keys
        self.min_internal_keys = (order + 1) // 2 - 1  # minimum keys in an INTERNAL node
        self.root = BPlusNode(is_leaf=True)

    def search(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i = i + 1
            node = node.children[i]

        for i in range(len(node.keys)):
            if node.keys[i] == key:
                return node.children[i]
        return None

    def insert(self, key, value):
        overflow = self._insert(self.root, key, value)

        if overflow is not None:
            middle_key, right_node = overflow
            new_root = BPlusNode(is_leaf=False)
            new_root.keys = [middle_key]
            new_root.children = [self.root, right_node]
            self.root = new_root

    def _insert(self, node, key, value):
        if node.is_leaf:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i = i + 1

            if i < len(node.keys) and node.keys[i] == key:
                node.children[i] = value  # key already exists, just update
                return None

            node.keys.insert(i, key)
            node.children.insert(i, value)
        else:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i = i + 1

            overflow = self._insert(node.children[i], key, value)
            if overflow is not None:
                middle_key, right_node = overflow
                node.keys.insert(i, middle_key)
                node.children.insert(i + 1, right_node)

        if len(node.keys) > self.max_keys:
            return self._split(node)
        return None

    def _split(self, node):
        middle = len(node.keys) // 2
        right_node = BPlusNode(is_leaf=node.is_leaf)

        if node.is_leaf:
            right_node.keys = node.keys[middle:]
            right_node.children = node.children[middle:]
            node.keys = node.keys[:middle]
            node.children = node.children[:middle]

            right_node.next_leaf = node.next_leaf
            node.next_leaf = right_node

            middle_key = right_node.keys[0]  # copied up, still kept in the leaf
        else:
            middle_key = node.keys[middle]
            right_node.keys = node.keys[middle + 1:]
            right_node.children = node.children[middle + 1:]
            node.keys = node.keys[:middle]
            node.children = node.children[:middle + 1]

        return (middle_key, right_node)

    def delete(self, key):
        if self.search(key) is None:
            print("Key", key, "not found")
            return

        self._delete(self.root, key)

        if not self.root.is_leaf and len(self.root.children) == 1:
            self.root = self.root.children[0]

    def _delete(self, node, key):
        if node.is_leaf:
            if key in node.keys:
                i = node.keys.index(key)
                node.keys.pop(i)
                node.children.pop(i)
            return

        i = 0
        while i < len(node.keys) and key >= node.keys[i]:
            i = i + 1

        self._delete(node.children[i], key)

        # compare the child with ITS OWN minimum (leaf and internal are different)
        if len(node.children[i].keys) < self._minimum_keys(node.children[i]):
            self._fix_shortage(node, i)

    def _minimum_keys(self, node):
        # a leaf follows the leaf rule
        if node.is_leaf:
            return self.min_keys
        # an internal node follows the smaller internal rule
        return self.min_internal_keys

    def _fix_shortage(self, node, i):
        has_left_sibling = i > 0
        has_right_sibling = i < len(node.children) - 1

        # a sibling can lend a key only if it has more than the minimum of its
        # own kind; the child and its siblings are the same kind of node, so
        # the child's minimum is the right number to compare with
        minimum = self._minimum_keys(node.children[i])
        left_ok = has_left_sibling and len(node.children[i - 1].keys) > minimum
        right_ok = has_right_sibling and len(node.children[i + 1].keys) > minimum

        if left_ok:
            self._borrow_from_left(node, i)
        elif right_ok:
            self._borrow_from_right(node, i)
        elif has_left_sibling:
            self._merge(node, i - 1)
        elif has_right_sibling:
            self._merge(node, i)
        # else: this node has only one child, nothing to borrow/merge here -
        # its own parent will fix it (or the tree shrinks if this is the root)

    def _borrow_from_left(self, node, i):
        child = node.children[i]
        left_sibling = node.children[i - 1]

        if child.is_leaf:
            key = left_sibling.keys.pop()
            value = left_sibling.children.pop()
            child.keys.insert(0, key)
            child.children.insert(0, value)
            node.keys[i - 1] = child.keys[0]
        else:
            down_key = node.keys[i - 1]
            moved_child = left_sibling.children.pop()
            node.keys[i - 1] = left_sibling.keys.pop()
            child.keys.insert(0, down_key)
            child.children.insert(0, moved_child)

    def _borrow_from_right(self, node, i):
        child = node.children[i]
        right_sibling = node.children[i + 1]

        if child.is_leaf:
            key = right_sibling.keys.pop(0)
            value = right_sibling.children.pop(0)
            child.keys.append(key)
            child.children.append(value)
            node.keys[i] = right_sibling.keys[0]
        else:
            down_key = node.keys[i]
            moved_child = right_sibling.children.pop(0)
            node.keys[i] = right_sibling.keys.pop(0)
            child.keys.append(down_key)
            child.children.append(moved_child)

    def _merge(self, node, i):
        left_child = node.children[i]
        right_child = node.children[i + 1]

        if left_child.is_leaf:
            left_child.keys.extend(right_child.keys)
            left_child.children.extend(right_child.children)
            left_child.next_leaf = right_child.next_leaf
        else:
            left_child.keys.append(node.keys[i])
            left_child.keys.extend(right_child.keys)
            left_child.children.extend(right_child.children)

        node.keys.pop(i)
        node.children.pop(i + 1)

    def traverse(self):
        # data only lives in the leaves, so walk to the left-most leaf
        # and then follow the linked leaves left to right
        node = self.root
        while not node.is_leaf:
            node = node.children[0]

        result = []
        while node is not None:
            for i in range(len(node.keys)):
                result.append((node.keys[i], node.children[i]))
            node = node.next_leaf
        return result
