"""
bst.py

Implements a Binary Search Tree (BST) that organizes bank transactions
by dollar amount, enabling efficient range queries.

A compliance officer can retrieve all transactions within a specified
amount range in O(log n + k) time, where k is the number of results,
rather than scanning the entire ledger in O(n) time.

Usage:
    from bst import TransactionBST
"""


# ---------------------------------------------------------------------------
# BST node
# ---------------------------------------------------------------------------

class BSTNode:
    """
    A single node in the transaction BST.

    The BST key is the transaction amount. Because multiple transactions
    can share the same amount, each node stores a list of transactions
    at that amount rather than a single record.

    Attributes
    ----------
    amount       : float     -- BST key (transaction dollar amount)
    transactions : list      -- all transactions with this amount
    left         : BSTNode   -- left child (amounts less than this node)
    right        : BSTNode   -- right child (amounts greater than this node)
    """

    def __init__(self, transaction):
        self.amount       = transaction.amount
        self.transactions = [transaction]
        self.left         = None
        self.right        = None


# ---------------------------------------------------------------------------
# Transaction BST
# ---------------------------------------------------------------------------

class TransactionBST:
    """
    Binary Search Tree organizing transactions by dollar amount.

    Supports insertion of new transactions and range queries that
    return all transactions with amounts between a lower and upper bound.
    This enables a compliance officer to run queries such as:
    "retrieve all transactions between $1,000 and $10,000."

    Operations
    ----------
    insert(transaction)        : O(log n) average, O(n) worst case
    range_query(low, high)     : O(log n + k) average, where k = results
    inorder()                  : O(n) -- sorted traversal by amount
    __len__()                  : O(1)

    Note: This is an unbalanced BST. In a production system a self-
    balancing tree such as an AVL tree or red-black tree would guarantee
    O(log n) worst-case performance. For the purposes of this proof of
    concept, an unbalanced BST is sufficient to demonstrate the range
    query functionality.
    """

    def __init__(self):
        self._root = None
        self._size = 0   # number of transaction records (not nodes)

    # -----------------------------------------------------------------------
    # Insert
    # -----------------------------------------------------------------------

    def insert(self, transaction):
        """
        Insert a transaction into the BST keyed on its amount.

        If a node with the same amount already exists, the transaction
        is appended to that node's list. Otherwise a new node is created.

        Time complexity: O(log n) average, O(n) worst case (degenerate tree)
        """
        if self._root is None:
            self._root = BSTNode(transaction)
        else:
            self._insert_recursive(self._root, transaction)
        self._size += 1

    def _insert_recursive(self, node, transaction):
        if transaction.amount < node.amount:
            if node.left is None:
                node.left = BSTNode(transaction)
            else:
                self._insert_recursive(node.left, transaction)
        elif transaction.amount > node.amount:
            if node.right is None:
                node.right = BSTNode(transaction)
            else:
                self._insert_recursive(node.right, transaction)
        else:
            # Same amount: append to existing node's list
            node.transactions.append(transaction)

    # -----------------------------------------------------------------------
    # Range query
    # -----------------------------------------------------------------------

    def range_query(self, low, high):
        """
        Return all transactions with amounts in [low, high] inclusive.

        The BST structure allows pruning: subtrees whose amounts fall
        entirely outside the range are never visited.

        Time complexity: O(log n + k) average where k = number of results

        Parameters
        ----------
        low  : float -- lower bound of the amount range (inclusive)
        high : float -- upper bound of the amount range (inclusive)

        Returns
        -------
        list of Transaction objects within the range, sorted by amount
        """
        results = []
        self._range_recursive(self._root, low, high, results)
        return results

    def _range_recursive(self, node, low, high, results):
        if node is None:
            return
        # Prune left subtree if all values there are below low
        if node.amount > low:
            self._range_recursive(node.left, low, high, results)
        # Include this node if it falls within range
        if low <= node.amount <= high:
            results.extend(node.transactions)
        # Prune right subtree if all values there are above high
        if node.amount < high:
            self._range_recursive(node.right, low, high, results)

    # -----------------------------------------------------------------------
    # Inorder traversal
    # -----------------------------------------------------------------------

    def inorder(self):
        """
        Yield all transactions in ascending order by amount.

        Time complexity: O(n)
        """
        yield from self._inorder_recursive(self._root)

    def _inorder_recursive(self, node):
        if node is None:
            return
        yield from self._inorder_recursive(node.left)
        for tx in node.transactions:
            yield tx
        yield from self._inorder_recursive(node.right)

    def __len__(self):
        return self._size

    def __repr__(self):
        return f"TransactionBST(transactions={self._size})"
