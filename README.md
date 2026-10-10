# B-Tree & B+ Tree in Python

A small library implementing two balanced search trees, plus a demo script.

| Structure | Where data lives | Extra feature |
|-----------|------------------|---------------|
| `BTree`   | Keys in every node | Sorted in-order traversal |
| `BPlusTree` | Key/value pairs only in leaves | Leaves linked together for fast sorted traversal |

Both trees support `search`, `insert`, `delete` and `traverse`, for any order of 3 or more.

## Files

- `btree_bplustree.py` - the library (`BTree`, `BPlusTree`)
- `main.py` - demo that builds both trees, searches, deletes and prints the results

## Requirements

Python 3. No external packages.

## Run the demo

```bash
python main.py
```

## Usage

```python
from btree_bplustree import BTree, BPlusTree

# B-Tree: stores keys
bt = BTree(order=4)
for k in [50, 30, 70, 20, 40]:
    bt.insert(k)
print(bt.search(40))     # True
bt.delete(30)
print(bt.traverse())     # [20, 40, 50, 70]

# B+ Tree: stores key -> value
bp = BPlusTree(order=4)
for k in [50, 30, 70, 20, 40]:
    bp.insert(k, "item-" + str(k))
print(bp.search(40))     # item-40
bp.delete(30)
print(bp.traverse())     # [(20, 'item-20'), (40, 'item-40'), (50, 'item-50'), (70, 'item-70')]
```

## API

| Method | BTree | BPlusTree |
|--------|-------|-----------|
| `insert` | `insert(key)` | `insert(key, value)` (inserting an existing key updates its value) |
| `search` | `search(key)` returns `True` / `False` | `search(key)` returns the value, or `None` |
| `delete` | `delete(key)` (prints a message if the key is missing) | same |
| `traverse` | list of keys in sorted order | list of `(key, value)` pairs in sorted order |

## How it works

**Order** is the maximum number of children a node can have, so a node holds at most `order - 1` keys.

**BTree**
- Minimum keys per non-root node: `ceil(order / 2) - 1`.
- Insert splits an overflowing node and pushes the middle key up.
- Delete removes a key from a leaf directly. For a key in an internal node, it swaps in the predecessor and deletes that from the left child.
- After the recursive delete returns, a child with too few keys is fixed by borrowing from a sibling or merging. The fix happens only after the delete returns, so a merge can never create an oversized node.

**BPlusTree**
- Leaves keep at least `order // 2` keys.
- Internal nodes keep at least `(order + 1) // 2 - 1` keys. The smaller minimum is needed because the separator key comes down when two internal nodes merge, and the merged node must still fit within `order - 1` keys.
- Leaf splits copy the first key of the new leaf up to the parent. Internal splits move the middle key up.
- Leaves are chained with `next_leaf`, so `traverse()` walks the leaf chain from left to right.

## Testing

The trees were checked with random insert and delete sequences for orders 3 to 10. After every step the checks were:
- no node exceeds `order - 1` keys
- no non-root node is under its minimum
- all leaves are at the same depth
- the traversal matches the expected sorted keys

Inserting 500 keys and deleting them all leaves an empty tree with a single leaf as the root.
