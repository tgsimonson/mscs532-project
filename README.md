# Bank Transaction Ledger: Developing and Optimizing Data Structures for Real-World Applications

**Course:** MSCS 532 — Algorithms and Data Structures  
**University of the Cumberlands**  
**Instructor:** Dr. Michael Solomon

---

## Overview

This project implements and optimizes a bank transaction ledger system across three phases. The system supports two primary user workflows: a fraud analyst retrieving specific transactions by ID, and a compliance officer querying transactions by dollar amount range. Three data structures work together to support these workflows efficiently.

---

## Files

| File | Description |
|---|---|
| `linked_list.py` | Append-only hash-chained singly linked list (audit ledger) |
| `hash_table.py` | Hash table with primary (tx_id) and secondary (account_id) indexes |
| `bst.py` | Self-balancing AVL tree for range queries by dollar amount |
| `demo.py` | Full demonstration, benchmarking, and stress tests |
| `performance_comparison.png` | Phase 2 vs Phase 3 benchmark chart (auto-generated) |
| `report.pdf` | Phase 3 written report (APA 7th edition) |

---

## How to Run

**Requirements:** Python 3.8+, matplotlib

```bash
pip install matplotlib
```

**Run full evaluation (correctness, benchmarks, stress tests, chart):**

```bash
python demo.py
```

---

## Data Structures

### Linked List — Tamper-Evident Audit Log
Each node stores a transaction and a SHA-256 hash of the previous node's hash concatenated with the current transaction data. Any modification to a historical record invalidates all subsequent hashes, making tampering detectable.

| Operation | Complexity |
|---|---|
| append | O(1) |
| traverse | O(n) |
| verify_integrity | O(n) |

### Hash Table — Transaction Index
Primary index maps transaction ID to Transaction record. Secondary index (Phase 3) maps account ID to all transactions for that account.

| Operation | Complexity |
|---|---|
| insert | O(1) amortized |
| lookup by tx_id | O(1) average |
| lookup by account_id | O(1) average |
| delete | O(1) average |

### AVL Tree — Range Query Index (Phase 3)
Replaced the Phase 2 unbalanced BST. Self-balancing guarantees O(log n) worst-case insert and range query regardless of insertion order. The unbalanced BST degraded to O(n) on sorted inputs, which is a realistic scenario in financial data ingestion.

| Operation | Complexity |
|---|---|
| insert | O(log n) guaranteed |
| range_query | O(log n + k) guaranteed |
| inorder traversal | O(n) |

---

## Project Phases

### Phase 1 — Design
Defined the application context (bank transaction ledger), selected data structures, and justified design choices. Original design used a linked list, hash table, and Merkle tree. Following feedback, the Merkle tree was replaced with a BST in Phase 2.

### Phase 2 — Proof of Concept
Implemented core operations for all three structures. Identified two bottlenecks: the unbalanced BST degraded to O(n) on sorted input, and account-level lookups required O(n) ledger traversal.

### Phase 3 — Optimization and Evaluation
- Replaced unbalanced BST with AVL tree: 129x speedup on sorted insertion at n=10,000 (5,639 ms vs 43.7 ms)
- Added secondary account index: 214x speedup on account lookup at n=10,000 (0.755 ms vs 0.0035 ms)
- Stress tested at 50,000 transactions: AVL height 19, consistent with O(log n)

---

## Reference

Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to algorithms* (4th ed.). Random House Publishing Services. https://reader.yuzu.com/books/9780262367509
