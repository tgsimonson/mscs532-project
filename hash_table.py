"""
hash_table.py

Implements a hash table that indexes bank transactions by their
transaction ID, enabling O(1) average-case retrieval.

Uses separate chaining for collision resolution. The table doubles
in size when the load factor exceeds 0.7 to maintain performance.

Usage:
    from hash_table import TransactionIndex
"""


# ---------------------------------------------------------------------------
# Transaction index (hash table with chaining)
# ---------------------------------------------------------------------------

class TransactionIndex:
    """
    Hash table mapping transaction IDs to their Transaction records.

    A fraud analyst or customer service representative can retrieve any
    specific transaction in O(1) average time without traversing the
    full ledger chain.

    Each slot in the table holds a list of (tx_id, transaction) pairs
    to handle collisions via separate chaining.

    Operations
    ----------
    insert(transaction)  : O(1) amortized -- index a new transaction
    lookup(tx_id)        : O(1) average   -- retrieve transaction by ID
    delete(tx_id)        : O(1) average   -- remove a transaction from index
    __len__()            : O(1)           -- number of indexed transactions
    __contains__(tx_id)  : O(1) average   -- membership test

    Space complexity: O(n) where n is the number of transactions stored.
    """

    INITIAL_SIZE  = 16
    LOAD_MAX      = 0.7

    def __init__(self):
        self._size  = self.INITIAL_SIZE
        self._count = 0
        self._table = [[] for _ in range(self._size)]

    # -----------------------------------------------------------------------
    # Hash function
    # -----------------------------------------------------------------------

    def _hash(self, tx_id):
        """Map a transaction ID string to a slot index."""
        return hash(tx_id) % self._size

    # -----------------------------------------------------------------------
    # Core operations
    # -----------------------------------------------------------------------

    def insert(self, transaction):
        """
        Insert a transaction into the index.

        If the transaction ID already exists, the record is updated.

        Time complexity: O(1) amortized (O(n) on resize, which is rare)
        """
        slot  = self._hash(transaction.tx_id)
        chain = self._table[slot]

        for i, (key, _) in enumerate(chain):
            if key == transaction.tx_id:
                chain[i] = (transaction.tx_id, transaction)
                return

        chain.append((transaction.tx_id, transaction))
        self._count += 1

        if self._load_factor() > self.LOAD_MAX:
            self._resize()

    def lookup(self, tx_id):
        """
        Retrieve the Transaction with the given ID.

        Returns the Transaction if found, or None if not present.

        Time complexity: O(1) average, O(n) worst case (degenerate chaining)
        """
        slot = self._hash(tx_id)
        for key, transaction in self._table[slot]:
            if key == tx_id:
                return transaction
        return None

    def delete(self, tx_id):
        """
        Remove the transaction with the given ID from the index.

        Returns True if the transaction was found and removed,
        False if it was not present.

        Time complexity: O(1) average
        """
        slot  = self._hash(tx_id)
        chain = self._table[slot]

        for i, (key, _) in enumerate(chain):
            if key == tx_id:
                chain.pop(i)
                self._count -= 1
                return True
        return False

    def __contains__(self, tx_id):
        return self.lookup(tx_id) is not None

    def __len__(self):
        return self._count

    # -----------------------------------------------------------------------
    # Load factor and resizing
    # -----------------------------------------------------------------------

    def _load_factor(self):
        return self._count / self._size

    def _resize(self):
        """
        Double the table size and rehash all entries.

        Time complexity: O(n) for a single resize.
        Amortized cost per insert over n operations: O(1).
        """
        old_table   = self._table
        self._size  = self._size * 2
        self._count = 0
        self._table = [[] for _ in range(self._size)]

        for chain in old_table:
            for _, transaction in chain:
                self.insert(transaction)

    def __repr__(self):
        return (f"TransactionIndex(slots={self._size}, "
                f"entries={self._count}, "
                f"load_factor={self._load_factor():.2f})")
