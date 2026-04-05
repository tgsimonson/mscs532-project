"""
demo.py

Phase 3: Optimization, Scaling, and Final Evaluation

Extends the Phase 2 demonstration with:
  1. Correctness verification of all optimized data structures
  2. Performance benchmarking: Phase 2 (unbalanced BST) vs Phase 3 (AVL)
     across increasing dataset sizes and adversarial insertion orders
  3. Account-level secondary index demonstration (new in Phase 3)
  4. Stress testing: sorted insertion, large datasets, edge cases

Usage:
    python demo.py

Outputs:
    performance_comparison.png
"""

import random
import time
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from linked_list import TransactionLedger, Transaction
from hash_table  import TransactionIndex
from bst         import TransactionAVL


# ---------------------------------------------------------------------------
# Phase 2 unbalanced BST (retained for comparison only)
# ---------------------------------------------------------------------------

class _UnbalancedBSTNode:
    def __init__(self, transaction):
        self.amount       = transaction.amount
        self.transactions = [transaction]
        self.left         = None
        self.right        = None

class UnbalancedBST:
    """Phase 2 unbalanced BST, kept for performance comparison."""
    def __init__(self):
        self._root = None
        self._size = 0

    def insert(self, transaction):
        self._root = self._insert(self._root, transaction)
        self._size += 1

    def _insert(self, node, transaction):
        if node is None:
            return _UnbalancedBSTNode(transaction)
        if transaction.amount < node.amount:
            node.left  = self._insert(node.left,  transaction)
        elif transaction.amount > node.amount:
            node.right = self._insert(node.right, transaction)
        else:
            node.transactions.append(transaction)
        return node

    def range_query(self, low, high):
        results = []
        self._range(self._root, low, high, results)
        return results

    def _range(self, node, low, high, results):
        if node is None:
            return
        if node.amount > low:
            self._range(node.left, low, high, results)
        if low <= node.amount <= high:
            results.extend(node.transactions)
        if node.amount < high:
            self._range(node.right, low, high, results)

    def __len__(self):
        return self._size


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def section(title):
    print(f"\n{'=' * 65}")
    print(f"  {title}")
    print('=' * 65)


def make_transaction(i, amount=None):
    amount = amount if amount is not None else random.uniform(10, 50000)
    acct   = f"ACC-{(i % 20) + 1:04d}"   # 20 distinct accounts
    return Transaction(f"TX{i:06d}", acct, round(amount, 2), "test")


def measure_ms(fn):
    start = time.perf_counter()
    fn()
    return (time.perf_counter() - start) * 1000


# ---------------------------------------------------------------------------
# 1. Correctness verification
# ---------------------------------------------------------------------------

def test_correctness():
    section("1. Correctness Verification")

    # AVL insert and range query
    avl = TransactionAVL()
    amounts = [500, 100, 800, 300, 700, 200, 900, 400, 600, 1000]
    txs = [Transaction(f"TX{i}", "ACC-001", float(a), "test")
           for i, a in enumerate(amounts)]
    for tx in txs:
        avl.insert(tx)

    inorder_amounts = [tx.amount for tx in avl.inorder()]
    expected        = sorted(float(a) for a in amounts)
    print(f"\n  AVL inorder sorted:  {'PASS' if inorder_amounts == expected else 'FAIL'}")
    print(f"  AVL tree height:     {avl.tree_height()} (log2(10) ≈ 3.3)")

    results = avl.range_query(300, 700)
    result_amounts = sorted(tx.amount for tx in results)
    print(f"  Range query [300,700]: {result_amounts} {'PASS' if result_amounts == [300.0,400.0,500.0,600.0,700.0] else 'FAIL'}")

    # AVL on sorted insertion (worst case for unbalanced BST)
    avl2 = TransactionAVL()
    for i in range(1, 101):
        avl2.insert(Transaction(f"TX{i}", "ACC-001", float(i), "test"))
    print(f"\n  AVL height after 100 sorted inserts: {avl2.tree_height()} (expected ~7, log2(100)≈6.6)")

    # Secondary account index
    idx = TransactionIndex()
    for i in range(10):
        tx = Transaction(f"TX{i:03d}", f"ACC-{i % 3:03d}", float(i * 100), "test")
        idx.insert(tx)
    acct0 = idx.lookup_by_account("ACC-000")
    print(f"\n  Account index lookup ACC-000: {len(acct0)} transactions {'PASS' if len(acct0) > 0 else 'FAIL'}")

    # Integrity check
    ledger = TransactionLedger()
    for i in range(5):
        ledger.append(Transaction(f"TX{i}", "ACC-001", float(i * 100), "test"))
    print(f"  Ledger integrity (unmodified): {'PASS' if ledger.verify_integrity() else 'FAIL'}")


# ---------------------------------------------------------------------------
# 2. Performance benchmark: Phase 2 BST vs Phase 3 AVL
# ---------------------------------------------------------------------------

def benchmark_bst_vs_avl():
    section("2. BST vs AVL Performance Benchmark")

    sizes = [100, 500, 1000, 5000, 10000]
    results = {
        "random": {"bst_insert": [], "avl_insert": [], "bst_query": [], "avl_query": []},
        "sorted": {"bst_insert": [], "avl_insert": [], "bst_query": [], "avl_query": []},
    }

    sys.setrecursionlimit(100000)

    print(f"\n  {'n':>7}  {'BST insert':>12}  {'AVL insert':>12}  "
          f"{'BST query':>12}  {'AVL query':>12}  Distribution")
    print("  " + "-" * 68)

    for dist in ["random", "sorted"]:
        for n in sizes:
            if dist == "random":
                txs = [make_transaction(i) for i in range(n)]
            else:
                # Sorted by amount: worst case for unbalanced BST
                txs = [Transaction(f"TX{i:06d}", "ACC-0001", float(i), "test")
                       for i in range(n)]

            bst = UnbalancedBST()
            avl = TransactionAVL()

            # Insert timing
            t_bst_i = measure_ms(lambda: [bst.insert(tx) for tx in txs])
            t_avl_i = measure_ms(lambda: [avl.insert(tx) for tx in txs])

            # Range query timing (middle 50% of range)
            lo = n * 0.25
            hi = n * 0.75
            t_bst_q = measure_ms(lambda: bst.range_query(lo, hi))
            t_avl_q = measure_ms(lambda: avl.range_query(lo, hi))

            results[dist]["bst_insert"].append(t_bst_i)
            results[dist]["avl_insert"].append(t_avl_i)
            results[dist]["bst_query"].append(t_bst_q)
            results[dist]["avl_query"].append(t_avl_q)

            print(f"  {n:>7}  {t_bst_i:>12.3f}  {t_avl_i:>12.3f}  "
                  f"{t_bst_q:>12.3f}  {t_avl_q:>12.3f}  {dist}")

    return sizes, results


# ---------------------------------------------------------------------------
# 3. Secondary index benchmark
# ---------------------------------------------------------------------------

def benchmark_account_index():
    section("3. Account Index vs Ledger Traversal")

    sizes = [100, 500, 1000, 5000, 10000]
    print(f"\n  {'n':>7}  {'Traversal (ms)':>16}  {'Index lookup (ms)':>18}  Speedup")
    print("  " + "-" * 56)

    traversal_times = []
    index_times     = []

    for n in sizes:
        ledger = TransactionLedger()
        index  = TransactionIndex()
        target = "ACC-0010"

        for i in range(n):
            tx = make_transaction(i)
            ledger.append(tx)
            index.insert(tx)
        # Add some known-account transactions
        for i in range(5):
            tx = Transaction(f"KNOWN{i}", target, float(i * 100), "known")
            ledger.append(tx)
            index.insert(tx)

        # Phase 2: traverse full ledger to find account
        t_trav = measure_ms(lambda: [
            tx for tx in ledger.traverse() if tx.account_id == target
        ])
        # Phase 3: direct account index lookup
        t_idx  = measure_ms(lambda: index.lookup_by_account(target))

        traversal_times.append(t_trav)
        index_times.append(t_idx)

        speedup = t_trav / t_idx if t_idx > 0 else float('inf')
        print(f"  {n:>7}  {t_trav:>16.3f}  {t_idx:>18.4f}  {speedup:>6.1f}x")

    return sizes, traversal_times, index_times


# ---------------------------------------------------------------------------
# 4. Stress tests
# ---------------------------------------------------------------------------

def stress_tests():
    section("4. Stress Tests")

    # Large dataset
    print("\n  Large dataset (50,000 transactions):")
    sys.setrecursionlimit(200000)
    avl   = TransactionAVL()
    idx   = TransactionIndex()
    ledger = TransactionLedger()
    N = 50000
    t = measure_ms(lambda: None)  # warm up
    start = time.perf_counter()
    for i in range(N):
        tx = make_transaction(i)
        avl.insert(tx)
        idx.insert(tx)
        ledger.append(tx)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"    Inserted {N} transactions in {elapsed:.1f} ms")
    print(f"    AVL height: {avl.tree_height()} (log2({N}) ≈ {N.bit_length() - 1})")
    print(f"    Index entries: {len(idx)}")
    print(f"    Ledger size: {len(ledger)}")

    # Range query on large dataset
    t_q = measure_ms(lambda: avl.range_query(10000, 40000))
    results = avl.range_query(10000, 40000)
    print(f"    Range query [10000,40000]: {len(results)} results in {t_q:.3f} ms")

    # Sorted insertion (AVL worst case stress)
    print("\n  Sorted insertion (10,000 elements, AVL worst-case structure):")
    avl2 = TransactionAVL()
    t_sorted = measure_ms(lambda: [
        avl2.insert(Transaction(f"TX{i}", "ACC-001", float(i), "sorted"))
        for i in range(10000)
    ])
    print(f"    AVL sorted insert: {t_sorted:.1f} ms, height={avl2.tree_height()}")

    # Unbalanced BST same input
    bst2 = UnbalancedBST()
    try:
        t_bst = measure_ms(lambda: [
            bst2.insert(Transaction(f"TX{i}", "ACC-001", float(i), "sorted"))
            for i in range(10000)
        ])
        print(f"    Unbalanced BST sorted insert: {t_bst:.1f} ms")
    except RecursionError:
        print(f"    Unbalanced BST: RecursionError on sorted input (stack overflow)")

    # Edge cases
    print("\n  Edge cases:")
    empty_avl = TransactionAVL()
    print(f"    Empty AVL range query: {empty_avl.range_query(0, 100)}")
    empty_idx = TransactionIndex()
    print(f"    Lookup missing key: {empty_idx.lookup('NOPE')}")
    print(f"    Delete missing key: {empty_idx.delete('NOPE')}")
    empty_ledger = TransactionLedger()
    print(f"    Empty ledger integrity: {empty_ledger.verify_integrity()}")

    # Tamper evidence
    ledger2 = TransactionLedger()
    for i in range(5):
        ledger2.append(Transaction(f"TX{i}", "ACC-001", float(i * 100), "test"))
    ledger2.head.next.transaction.amount = 999999.0
    print(f"    Tamper detection: {'PASS' if not ledger2.verify_integrity() else 'FAIL'}")


# ---------------------------------------------------------------------------
# Chart generation
# ---------------------------------------------------------------------------

def generate_chart(sizes, bst_avl_results, acct_sizes, trav_times, idx_times):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Chart 1: BST vs AVL insert (sorted input)
    axes[0].plot(sizes, bst_avl_results["sorted"]["bst_insert"],
                 "o-", color="tomato",    label="Unbalanced BST (Phase 2)")
    axes[0].plot(sizes, bst_avl_results["sorted"]["avl_insert"],
                 "s-", color="steelblue", label="AVL Tree (Phase 3)")
    axes[0].set_title("Insert Time — Sorted Input")
    axes[0].set_xlabel("Number of Transactions")
    axes[0].set_ylabel("Time (ms)")
    axes[0].legend(fontsize=8)
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)

    # Chart 2: BST vs AVL insert (random input)
    axes[1].plot(sizes, bst_avl_results["random"]["bst_insert"],
                 "o-", color="tomato",    label="Unbalanced BST (Phase 2)")
    axes[1].plot(sizes, bst_avl_results["random"]["avl_insert"],
                 "s-", color="steelblue", label="AVL Tree (Phase 3)")
    axes[1].set_title("Insert Time — Random Input")
    axes[1].set_xlabel("Number of Transactions")
    axes[1].set_ylabel("Time (ms)")
    axes[1].legend(fontsize=8)
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)

    # Chart 3: Account traversal vs index lookup
    axes[2].plot(acct_sizes, trav_times,
                 "o-", color="tomato",    label="Full traversal (Phase 2)")
    axes[2].plot(acct_sizes, idx_times,
                 "s-", color="steelblue", label="Account index (Phase 3)")
    axes[2].set_title("Account Lookup: Traversal vs Index")
    axes[2].set_xlabel("Number of Transactions")
    axes[2].set_ylabel("Time (ms)")
    axes[2].legend(fontsize=8)
    axes[2].grid(axis="y", linestyle="--", alpha=0.4)

    plt.suptitle(
        "Phase 2 vs Phase 3: Performance Comparison",
        fontsize=13, fontweight="bold"
    )
    plt.tight_layout()
    plt.savefig("performance_comparison.png", dpi=150, bbox_inches="tight")
    print("\nChart saved: performance_comparison.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Bank Transaction Ledger — Phase 3 Evaluation")
    print("MSCS 532: Algorithms and Data Structures")

    test_correctness()
    sizes, bst_avl_results = benchmark_bst_vs_avl()
    acct_sizes, trav_times, idx_times = benchmark_account_index()
    stress_tests()
    generate_chart(sizes, bst_avl_results, acct_sizes, trav_times, idx_times)

    print(f"\n{'=' * 65}")
    print("  Phase 3 evaluation complete.")
    print('=' * 65)
