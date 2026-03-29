"""
demo.py

Proof-of-concept demonstration of the bank transaction ledger system.

Simulates the three core workflows:
  1. A teller appending new transactions to the ledger (linked list)
  2. A fraud analyst retrieving a specific transaction by ID (hash table)
  3. A compliance officer querying transactions by amount range (BST)

Also demonstrates tamper-evidence detection and edge case handling.

Usage:
    python demo.py
"""

from linked_list import TransactionLedger, Transaction
from hash_table  import TransactionIndex
from bst         import TransactionBST


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_TRANSACTIONS = [
    ("TX001", "ACC-1001",   250.00, "ATM withdrawal"),
    ("TX002", "ACC-2045",  1500.00, "wire transfer"),
    ("TX003", "ACC-1001",    45.75, "debit card purchase"),
    ("TX004", "ACC-3087",  8200.00, "payroll deposit"),
    ("TX005", "ACC-2045",   320.50, "online bill pay"),
    ("TX006", "ACC-4412", 15000.00, "mortgage payment"),
    ("TX007", "ACC-1001",   980.00, "check deposit"),
    ("TX008", "ACC-3087",   125.00, "ATM withdrawal"),
    ("TX009", "ACC-5501",  4750.00, "wire transfer"),
    ("TX010", "ACC-2045",    60.00, "debit card purchase"),
]


def build_system():
    """Build and populate all three data structures."""
    ledger = TransactionLedger()
    index  = TransactionIndex()
    bst    = TransactionBST()

    for tx_id, account, amount, desc in SAMPLE_TRANSACTIONS:
        tx = Transaction(tx_id, account, amount, desc)
        ledger.append(tx)
        index.insert(tx)
        bst.insert(tx)

    return ledger, index, bst


# ---------------------------------------------------------------------------
# Test 1: Ledger append and traversal
# ---------------------------------------------------------------------------

def test_ledger(ledger):
    section("TEST 1: Ledger — Append and Traversal")

    print(f"\n  {ledger}")
    print(f"\n  Chronological transaction log:")
    print(f"  {'TX ID':<8} {'Account':<12} {'Amount':>10}  Description")
    print("  " + "-" * 50)

    for tx in ledger.traverse():
        print(f"  {tx.tx_id:<8} {tx.account_id:<12} {tx.amount:>10.2f}  {tx.description}")

    # Integrity check
    intact = ledger.verify_integrity()
    print(f"\n  Integrity check (unmodified): {'PASS' if intact else 'FAIL'}")


# ---------------------------------------------------------------------------
# Test 2: Tamper-evidence detection
# ---------------------------------------------------------------------------

def test_tamper_detection(ledger):
    section("TEST 2: Tamper-Evidence Detection")

    # Silently modify a historical transaction amount
    node = ledger.head.next   # TX002
    original_amount = node.transaction.amount
    node.transaction.amount = 999999.00

    intact = ledger.verify_integrity()
    print(f"\n  Modified TX002 amount from {original_amount} to 999999.00")
    print(f"  Integrity check after modification: {'PASS' if intact else 'FAIL -- tampering detected'}")

    # Restore original value
    node.transaction.amount = original_amount
    intact = ledger.verify_integrity()
    print(f"  Integrity check after restoration:  {'PASS' if intact else 'FAIL'}")


# ---------------------------------------------------------------------------
# Test 3: Hash table lookup
# ---------------------------------------------------------------------------

def test_hash_table(index):
    section("TEST 3: Hash Table — Transaction Lookup")

    print(f"\n  {index}")

    # Successful lookups
    for tx_id in ["TX001", "TX006", "TX010"]:
        result = index.lookup(tx_id)
        if result:
            print(f"\n  lookup('{tx_id}') -> {result}")
        else:
            print(f"\n  lookup('{tx_id}') -> NOT FOUND")

    # Unsuccessful lookup
    result = index.lookup("TX999")
    print(f"\n  lookup('TX999') -> {'NOT FOUND' if result is None else result}")

    # Membership test
    print(f"\n  'TX004' in index: {'TX004' in index}")
    print(f"  'TX999' in index: {'TX999' in index}")

    # Delete and verify
    deleted = index.delete("TX005")
    print(f"\n  delete('TX005') -> {deleted}")
    print(f"  lookup('TX005') after delete -> {index.lookup('TX005')}")
    print(f"  Index size after delete: {len(index)}")


# ---------------------------------------------------------------------------
# Test 4: BST range query
# ---------------------------------------------------------------------------

def test_bst(bst):
    section("TEST 4: BST — Compliance Range Query")

    print(f"\n  {bst}")

    # Inorder traversal — confirms sorted order
    print(f"\n  All transactions sorted by amount (inorder traversal):")
    print(f"  {'TX ID':<8} {'Amount':>10}  Description")
    print("  " + "-" * 35)
    for tx in bst.inorder():
        print(f"  {tx.tx_id:<8} {tx.amount:>10.2f}  {tx.description}")

    # Range queries
    queries = [
        (100.00,  500.00),
        (1000.00, 9000.00),
        (10000.00, 20000.00),
        (0.00, 50.00),          # should return nothing
    ]

    for low, high in queries:
        results = bst.range_query(low, high)
        print(f"\n  range_query({low:.2f}, {high:.2f}) -> {len(results)} result(s):")
        for tx in results:
            print(f"    {tx.tx_id}  ${tx.amount:.2f}  {tx.description}")
        if not results:
            print(f"    (no transactions in this range)")


# ---------------------------------------------------------------------------
# Test 5: Edge cases
# ---------------------------------------------------------------------------

def test_edge_cases():
    section("TEST 5: Edge Cases")

    # Empty ledger
    empty_ledger = TransactionLedger()
    print(f"\n  Empty ledger integrity check: {empty_ledger.verify_integrity()}")
    print(f"  Empty ledger length: {len(empty_ledger)}")
    print(f"  Empty ledger traversal: {list(empty_ledger.traverse())}")

    # Empty index
    empty_index = TransactionIndex()
    print(f"\n  Lookup on empty index: {empty_index.lookup('TX001')}")
    print(f"  Delete on empty index: {empty_index.delete('TX001')}")

    # Empty BST range query
    empty_bst = TransactionBST()
    print(f"\n  Range query on empty BST: {empty_bst.range_query(0, 1000)}")

    # Single transaction
    single = Transaction("TX_SINGLE", "ACC-0001", 100.00, "test")
    single_ledger = TransactionLedger()
    single_ledger.append(single)
    print(f"\n  Single-transaction ledger integrity: {single_ledger.verify_integrity()}")

    # Duplicate transaction ID in index (upsert behavior)
    idx = TransactionIndex()
    tx1 = Transaction("TX_DUP", "ACC-0001", 100.00, "original")
    tx2 = Transaction("TX_DUP", "ACC-0001", 200.00, "updated")
    idx.insert(tx1)
    idx.insert(tx2)
    result = idx.lookup("TX_DUP")
    print(f"\n  Duplicate ID upsert — stored amount: {result.amount} "
          f"(expected 200.00, {'PASS' if result.amount == 200.00 else 'FAIL'})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Bank Transaction Ledger — Proof of Concept Demo")
    print("MSCS 532: Algorithms and Data Structures")

    ledger, index, bst = build_system()

    test_ledger(ledger)
    test_tamper_detection(ledger)
    test_hash_table(index)
    test_bst(bst)
    test_edge_cases()

    print(f"\n{'=' * 60}")
    print("  All tests complete.")
    print('=' * 60)
