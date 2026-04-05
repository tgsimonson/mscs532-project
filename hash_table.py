"""
hash_table.py

Phase 3 Optimization: Extends the Phase 2 hash table with a secondary
index mapping account IDs to all transactions for that account.

Phase 2 identified that retrieving all transactions for a specific account
required a full O(n) ledger traversal since the primary index only supported
lookup by transaction ID. The secondary index resolves this by maintaining
a separate hash table keyed on account_id, enabling O(1) average-case
retrieval of all transactions belonging to a given account.

Both indexes are kept synchronized on every insert and delete.

Usage:
    from hash_table import TransactionIndex
"""


# ---------------------------------------------------------------------------
# Transaction index (primary + secondary hash tables)
# ---------------------------------------------------------------------------

class TransactionIndex:
    """
    Dual hash table providing O(1) average-case lookup by both
    transaction ID and account ID.

    Primary index:   tx_id     -> Transaction
    Secondary index: account_id -> list of Transactions

    Both indexes are updated atomically on every insert and delete,
    ensuring they remain consistent with each other.

    Operations
    ----------
    insert(transaction)          : O(1) amortized
    lookup(tx_id)                : O(1) average
    lookup_by_account(account_id): O(1) average, returns list
    delete(tx_id)                : O(1) average
    __len__()                    : O(1)
    __contains__(tx_id)          : O(1) average

    Space complexity: O(n) for both indexes combined.
    """

    INITIAL_SIZE = 16
    LOAD_MAX     = 0.7

    def __init__(self):
        # Primary index: tx_id -> Transaction
        self._size    = self.INITIAL_SIZE
        self._count   = 0
        self._table   = [[] for _ in range(self._size)]

        # Secondary index: account_id -> list of Transactions
        # Uses Python dict for simplicity; could be a second custom
        # hash table if full control over hashing is required.
        self._account_index = {}

    # -----------------------------------------------------------------------
    # Hash function (primary index)
    # -----------------------------------------------------------------------

    def _hash(self, tx_id):
        """Map a transaction ID string to a slot index."""
        return hash(tx_id) % self._size

    # -----------------------------------------------------------------------
    # Insert
    # -----------------------------------------------------------------------

    def insert(self, transaction):
        """
        Insert a transaction into both the primary and secondary indexes.

        If the transaction ID already exists in the primary index, both
        indexes are updated to reflect the new record.

        Time complexity: O(1) amortized
        """
        slot  = self._hash(transaction.tx_id)
        chain = self._table[slot]

        for i, (key, old_tx) in enumerate(chain):
            if key == transaction.tx_id:
                # Update primary index
                chain[i] = (transaction.tx_id, transaction)
                # Update secondary index: remove old, add new
                self._account_remove(old_tx)
                self._account_add(transaction)
                return

        # New transaction
        chain.append((transaction.tx_id, transaction))
        self._count += 1
        self._account_add(transaction)

        if self._load_factor() > self.LOAD_MAX:
            self._resize()

    def _account_add(self, transaction):
        """Add transaction to secondary account index."""
        acct = transaction.account_id
        if acct not in self._account_index:
            self._account_index[acct] = []
        self._account_index[acct].append(transaction)

    def _account_remove(self, transaction):
        """Remove transaction from secondary account index."""
        acct = transaction.account_id
        if acct in self._account_index:
            self._account_index[acct] = [
                t for t in self._account_index[acct]
                if t.tx_id != transaction.tx_id
            ]
            if not self._account_index[acct]:
                del self._account_index[acct]

    # -----------------------------------------------------------------------
    # Lookup
    # -----------------------------------------------------------------------

    def lookup(self, tx_id):
        """
        Retrieve the Transaction with the given ID.
        Returns None if not found.
        Time complexity: O(1) average.
        """
        slot = self._hash(tx_id)
        for key, transaction in self._table[slot]:
            if key == tx_id:
                return transaction
        return None

    def lookup_by_account(self, account_id):
        """
        Retrieve all transactions for the given account ID.

        Phase 3 addition: O(1) average lookup by account rather than
        O(n) full ledger traversal required in Phase 2.

        Returns a list of Transaction objects (empty list if none found).
        Time complexity: O(1) average to retrieve the list.
        """
        return list(self._account_index.get(account_id, []))

    # -----------------------------------------------------------------------
    # Delete
    # -----------------------------------------------------------------------

    def delete(self, tx_id):
        """
        Remove the transaction from both indexes.
        Returns True if deleted, False if not found.
        Time complexity: O(1) average.
        """
        slot  = self._hash(tx_id)
        chain = self._table[slot]

        for i, (key, transaction) in enumerate(chain):
            if key == tx_id:
                chain.pop(i)
                self._count -= 1
                self._account_remove(transaction)
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
        Double the primary table and rehash all entries.
        Secondary index does not require rehashing since it uses
        Python's built-in dict.
        Time complexity: O(n) per resize, O(1) amortized per insert.
        """
        old_table      = self._table
        self._size     = self._size * 2
        self._count    = 0
        self._table    = [[] for _ in range(self._size)]
        # Reset secondary index and rebuild from primary
        self._account_index = {}

        for chain in old_table:
            for _, transaction in chain:
                slot = self._hash(transaction.tx_id)
                self._table[slot].append((transaction.tx_id, transaction))
                self._count += 1
                self._account_add(transaction)

    def __repr__(self):
        return (f"TransactionIndex(slots={self._size}, "
                f"entries={self._count}, "
                f"accounts={len(self._account_index)}, "
                f"load_factor={self._load_factor():.2f})")
