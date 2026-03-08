---
title: Chapter 16. Distributed Synchronisation 
created: 2025-03-16
tags:
    - operatingsystem
---

Hub: [[engineering]]

> Part of the [[series]]

### Event Ordering

1. The Happened-Before Relation
2. Implementation

### Mutual Exclusion

1. Centralised Approach
2. Fully Distributed Approach
3. Token-Passing Approach

### Atomicity

1. The Two-Phase Commit (2PC) Protocol
2. Failure handling in 2PC
    1. Failure of a participating site
    2. Failure of the coordinator
    3. Failure of the network

### Concurrency Control

1. Locking protocols
    1. Nonreplicated scheme
    2. Single-coordinator approach
    3. Majority protocol 
    4. Biased protocol 

2. Timestamping
    1. Generation of unique timestamps 
    2. Timestamp-ordering scheme 

### Deadlock handling

1. Deadlock prevention and avoidance
2. Deadlock detection
    1. Centralised approach 
    2. Fully distributed approach 

### Election Algorithms

1. The Bully Algorithm 
2. The Ring Algorithm 

### Reaching Agreement

1. Unreliable communications
2. Faulty processes 
