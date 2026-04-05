"""
bst.py

Phase 3 Optimization: Replaces the unbalanced Binary Search Tree from
Phase 2 with a self-balancing AVL tree.

Phase 2 identified that the unbalanced BST degrades to O(n) insert and
range query time when transactions are inserted in sorted order by amount,
which is a realistic scenario (e.g., ingesting a pre-sorted transaction
feed). The AVL tree guarantees O(log n) worst-case time for all operations
by maintaining a balance factor at every node and rotating when necessary.

The TransactionAVL class exposes the same public interface as the Phase 2
TransactionBST so that the rest of the system requires no changes.

Usage:
    from bst import TransactionAVL
"""


# ---------------------------------------------------------------------------
# AVL node
# ---------------------------------------------------------------------------

class AVLNode:
    """
    A single node in the AVL tree.

    Stores all transactions at a given dollar amount (duplicates allowed)
    plus the height of the subtree rooted at this node, which is used to
    compute the balance factor and trigger rotations.

    Attributes
    ----------
    amount       : float    -- AVL key (transaction dollar amount)
    transactions : list     -- all transactions with this amount
    left         : AVLNode  -- left child
    right        : AVLNode  -- right child
    height       : int      -- height of this subtree (leaf = 1)
    """

    def __init__(self, transaction):
        self.amount       = transaction.amount
        self.transactions = [transaction]
        self.left         = None
        self.right        = None
        self.height       = 1


# ---------------------------------------------------------------------------
# AVL Tree
# ---------------------------------------------------------------------------

class TransactionAVL:
    """
    Self-balancing AVL tree organizing transactions by dollar amount.

    The AVL property: for every node, the heights of its left and right
    subtrees differ by at most 1. After each insert, the tree rebalances
    itself via single and double rotations, maintaining O(log n) height.

    This replaces the Phase 2 unbalanced BST, which degraded to O(n) on
    sorted inputs. The AVL tree guarantees O(log n) for all operations
    regardless of insertion order.

    Operations
    ----------
    insert(transaction)     : O(log n) worst case
    range_query(low, high)  : O(log n + k) worst case, k = results
    inorder()               : O(n)
    tree_height()           : O(1)
    __len__()               : O(1)
    """

    def __init__(self):
        self._root = None
        self._size = 0

    # -----------------------------------------------------------------------
    # Height and balance helpers
    # -----------------------------------------------------------------------

    def _height(self, node):
        return node.height if node else 0

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right)

    def _update_height(self, node):
        node.height = 1 + max(self._height(node.left),
                               self._height(node.right))

    # -----------------------------------------------------------------------
    # Rotations
    # -----------------------------------------------------------------------

    def _rotate_right(self, y):
        """
        Right rotation around y. Used when left subtree is too tall.

             y                x
            / \\              / \\
           x   T3    =>    T1   y
          / \\                  / \\
        T1   T2              T2   T3
        """
        x       = y.left
        T2      = x.right
        x.right = y
        y.left  = T2
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x):
        """
        Left rotation around x. Used when right subtree is too tall.

           x                  y
          / \\                / \\
        T1   y      =>      x   T3
            / \\            / \\
          T2   T3        T1   T2
        """
        y       = x.right
        T2      = y.left
        y.left  = x
        x.right = T2
        self._update_height(x)
        self._update_height(y)
        return y

    def _rebalance(self, node):
        """Rebalance node if its balance factor is outside [-1, 1]."""
        self._update_height(node)
        bf = self._balance_factor(node)

        # Left-heavy
        if bf > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right-heavy
        if bf < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # -----------------------------------------------------------------------
    # Insert
    # -----------------------------------------------------------------------

    def insert(self, transaction):
        """
        Insert a transaction keyed on its dollar amount.
        Rebalances the tree after every structural insertion.
        Time complexity: O(log n) worst case.
        """
        self._root = self._insert_recursive(self._root, transaction)
        self._size += 1

    def _insert_recursive(self, node, transaction):
        if node is None:
            return AVLNode(transaction)
        if transaction.amount < node.amount:
            node.left  = self._insert_recursive(node.left,  transaction)
        elif transaction.amount > node.amount:
            node.right = self._insert_recursive(node.right, transaction)
        else:
            node.transactions.append(transaction)
            return node  # duplicate amount: no structural change
        return self._rebalance(node)

    # -----------------------------------------------------------------------
    # Range query
    # -----------------------------------------------------------------------

    def range_query(self, low, high):
        """
        Return all transactions with amounts in [low, high] inclusive.
        Prunes subtrees outside the range to avoid unnecessary traversal.
        Time complexity: O(log n + k) worst case, k = number of results.
        """
        results = []
        self._range_recursive(self._root, low, high, results)
        return results

    def _range_recursive(self, node, low, high, results):
        if node is None:
            return
        if node.amount > low:
            self._range_recursive(node.left, low, high, results)
        if low <= node.amount <= high:
            results.extend(node.transactions)
        if node.amount < high:
            self._range_recursive(node.right, low, high, results)

    # -----------------------------------------------------------------------
    # Inorder traversal
    # -----------------------------------------------------------------------

    def inorder(self):
        """Yield all transactions in ascending order by amount. O(n)."""
        yield from self._inorder_recursive(self._root)

    def _inorder_recursive(self, node):
        if node is None:
            return
        yield from self._inorder_recursive(node.left)
        for tx in node.transactions:
            yield tx
        yield from self._inorder_recursive(node.right)

    def tree_height(self):
        """Return the height of the AVL tree. Expected O(log n)."""
        return self._height(self._root)

    def __len__(self):
        return self._size

    def __repr__(self):
        return (f"TransactionAVL(transactions={self._size}, "
                f"height={self.tree_height()})")
