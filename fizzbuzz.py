"""
FIZZBUZZ
Copyright 2025-present NAVER Corp.
The 3-Clause BSD License

fizzbuzz: A simple demonstration of how to use predicates for an intemporal example.
"""

from predicate import p_check, predicate

@predicate()
def fizzbuzz(i):
    p_check(i%15==0)
    print("fizzbuzz", end = " ")


@predicate()
def fizzbuzz(i):
    p_check(i%3==0)
    print("fizz", end = " ")

@predicate()
def fizzbuzz(i):
    p_check(i%5==0)
    print("buzz", end = " ")


@predicate()
def fizzbuzz(i):
    print(i, end = " ")

for i in range(1,200,1):
    fizzbuzz(i)
print()
