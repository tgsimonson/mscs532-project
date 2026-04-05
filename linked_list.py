"""
linked_list.py

Implements an append-only singly linked list representing a bank's
chronological transaction ledger.

Each node stores a Transaction record and a SHA-256 hash of the
previous node's hash concatenated with the current transaction data.
This makes any modification to a historical record detectable when
the chain is verified -- the ledger is tamper-evident.

No changes were made to this module in Phase 3. The linked list
performed within acceptable bounds during Phase 2 benchmarking, and
its O(1) append and O(n) traversal/verify operations are appropriate
for the append-only audit log use case.

Usage:
    from linked_list import TransactionLedger, Transaction
"""

import hashlib
import time


# ---------------------------------------------------------------------------
# Transaction record
# ---------------------------------------------------------------------------

class Transaction:
    """
    Represents a single bank transaction.

    Attributes
    ----------
    tx_id       : str   -- unique transaction identifier
    account_id  : str   -- account number associated with the transaction
    amount      : float -- transaction amount in dollars
    timestamp   : float -- Unix timestamp of the transaction
    description : str   -- short description
    """

    def __init__(self, tx_id, account_id, amount, description=""):
        self.tx_id       = tx_id
        self.account_id  = account_id
        self.amount      = amount
        self.timestamp   = time.time()
        self.description = description

    def to_string(self):
        """Return a canonical string representation for hashing."""
        return (f"{self.tx_id}|{self.account_id}|"
                f"{self.amount}|{self.timestamp}|{self.description}")

    def __repr__(self):
        return (f"Transaction(id={self.tx_id}, account={self.account_id}, "
                f"amount={self.amount:.2f}, desc='{self.description}')")


# ---------------------------------------------------------------------------
# Ledger node
# ---------------------------------------------------------------------------

class LedgerNode:
    """
    A single node in the transaction ledger chain.

    Stores one Transaction and a hash that depends on both the transaction
    data and the hash of the preceding node. This chain of hashes makes
    the ledger tamper-evident.

    Attributes
    ----------
    transaction : Transaction -- the stored transaction record
    prev_hash   : str         -- hash of the preceding node
    node_hash   : str         -- SHA-256 hash of prev_hash + transaction data
    next        : LedgerNode  -- pointer to the next node
    """

    GENESIS_HASH = "0" * 64

    def __init__(self, transaction, prev_hash=None):
        self.transaction = transaction
        self.prev_hash   = prev_hash or self.GENESIS_HASH
        self.node_hash   = self._compute_hash()
        self.next        = None

    def _compute_hash(self):
        content = self.prev_hash + self.transaction.to_string()
        return hashlib.sha256(content.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Transaction ledger (singly linked list)
# ---------------------------------------------------------------------------

class TransactionLedger:
    """
    Append-only singly linked list representing a bank transaction ledger.

    Operations
    ----------
    append(transaction)  : O(1)
    traverse()           : O(n)
    verify_integrity()   : O(n)
    __len__()            : O(1)
    """

    def __init__(self):
        self.head  = None
        self.tail  = None
        self._size = 0

    def append(self, transaction):
        """Append a new transaction. Time complexity: O(1)."""
        prev_hash = self.tail.node_hash if self.tail else None
        node = LedgerNode(transaction, prev_hash)
        if self.head is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._size += 1

    def traverse(self):
        """Yield each Transaction in chronological order. O(n)."""
        current = self.head
        while current:
            yield current.transaction
            current = current.next

    def verify_integrity(self):
        """
        Recompute each node's hash and confirm it matches the stored value.
        Returns True if intact, False if any tampering is detected. O(n).
        """
        current = self.head
        while current:
            if current.node_hash != current._compute_hash():
                return False
            if current.next and current.next.prev_hash != current.node_hash:
                return False
            current = current.next
        return True

    def __len__(self):
        return self._size

    def __repr__(self):
        return f"TransactionLedger(size={self._size})"
