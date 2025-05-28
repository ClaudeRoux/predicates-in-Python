# Prolog-like Logic in Python
This document describes the functionality of the @predicate, @principles, and @p_prolog decorators, which enable Prolog-like declarative programming in Python.

## @predicate Decorator
The @predicate decorator allows you to define multiple clauses for a single predicate name. It implements an OR-like logic with implicit cut.

**Purpose**: To define a set of alternative conditions (clauses) for a given predicate. The first successful clause determines the predicate's outcome, and no further alternatives are considered. This is useful for modeling "if-then-else" scenarios or finding the first matching rule.

### How it Works:

* Clauses: Multiple functions with the same name, each decorated with @predicate(), act as individual clauses.

* Guards: An optional guard function can be provided (@predicate(guard=...)) to determine if a clause should be attempted. If the guard returns False, that clause is skipped, and the next one is tried.

* p_check(condition) / p_fail(): Used within a clause to assert conditions. If condition is False or p_fail() is called, the clause fails by raising PredicateFailed. This triggers backtracking to the next available clause.

* Success: A clause succeeds if its guard passes and its body executes completely without raising PredicateFailed.

* Implicit Cut: Upon a clause's success, no further clauses for that predicate are attempted. The predicate immediately returns True.

```Python
Example:

from predicate import predicate, p_check

@predicate(guard=lambda x: isinstance(x, int) and x > 0)
def describe_number(x):
    p_check(x % 2 == 0)
    print(f"{x} is a positive even number.")

@predicate(guard=lambda x: isinstance(x, int) and x > 0)
def describe_number(x):
    p_check(x % 2 != 0)
    print(f"{x} is a positive odd number.")

@predicate()
def describe_number(x):
    print(f"{x} is not a positive integer.")

describe_number(4)   # Output: "4 is a positive even number." (only first clause runs)
describe_number(7)   # Output: "7 is a positive odd number." (first clause fails, second runs)
describe_number(-5)  # Output: "-5 is not a positive integer." (first two guards fail, default runs)

Return Value: Returns True if any clause succeeds; False if all clauses fail.
````

## @principles Decorator
The @principles decorator implements a strict AND-like logic.

Purpose: To define a set of mandatory conditions (clauses) that all must be satisfied for the predicate to succeed. This is ideal for validating an entity against a set of rules where all rules must pass.

### How it Works:

All Clauses Required: All registered clauses for a given principles name must succeed sequentially. The order of definition matters.

* Guards: If a clause's guard fails, the entire principles immediately fails, and subsequent clauses are not checked.

* p_check(condition) / p_fail(): If a clause's body raises PredicateFailed, the entire principles immediately fails, and subsequent clauses are not checked.

Example:

```Python
from predicate import principles, p_check

@principles(guard=lambda age: isinstance(age, int))
def is_eligible_voter(age):
    p_check(age >= 18, "Must be at least 18 years old.")
    print("Age requirement met.")

@principles(guard=lambda age: isinstance(age, int))
def is_eligible_voter(age):
    p_check(age < 120, "Age must be less than 120.")
    print("Max age requirement met.")

print(is_eligible_voter(25)) # Output: "Age requirement met." "Max age requirement met." True
print(is_eligible_voter(16)) # Output: "Age requirement met." False (fails first p_check)
print(is_eligible_voter(130))# Output: "Age requirement met." "Max age requirement met." False (fails second p_check)

Return Value: Returns True only if all clauses (both their guards and bodies) succeed; False if any clause fails.
```


## @p_prolog Decorator
The @p_prolog decorator enables Prolog-like logic with explicit backtracking and the ability to "cut" the search for further solutions. Decorated functions must be Python generators, yielding solutions as they are found.

### Purpose: 
To model problems that require finding multiple solutions, where each solution path might involve complex conditional logic and explicit control over the search space (like Prolog's cut). It's suitable for scenarios like rule-based systems that need to explore all possible successful paths, or generate all valid combinations based on a set of rules.

### How it Works:
* Generator Clauses: Each clause for a p_prolog predicate is a Python generator function (it must use yield). Instead of returning True or False, it yields solutions or values as it successfully finds them.

* Guards: Similar to @predicate and @principles, an optional guard function can be provided. If the guard returns False or raises an exception, the current clause is skipped, and the search proceeds to the next clause.

* p_check(condition) / p_fail(): These functions are used within the generator clause's body. If p_check(condition) evaluates to False or p_fail() is called, a PredicateFailed exception is raised. This signals that the current path within the clause has failed, and the p_prolog wrapper will attempt to backtrack to the next potential solution path or clause.

* p_cut(): This special function, when yielded from within a generator clause (yield p_cut()), acts as a Prolog-like "cut". When encountered, it signifies that no further clauses for the current predicate name should be attempted, even if the current clause might fail later or produce no more solutions. The p_cut() itself is not collected as a solution.

* Collecting Solutions: The p_prolog wrapper iterates through all applicable clauses and their generated solutions. It collects all yielded values (that are not the cut sentinel) into a list.

* Backtracking: If a clause's body (generator) raises PredicateFailed or any other exception, or if its guard fails, the system automatically "backtracks" and attempts the next clause registered for the same predicate name.

### Cut Behavior: 
If p_cut() is yielded by any clause, the system will stop trying any subsequent clauses for that predicate, regardless of whether the current clause produces more results or eventually fails. However, the current clause's generator continues to execute after the yield p_cut() statement. This allows the current clause to potentially yield more results before it finishes.

Example:

```python
from predicate import p_prolog, p_check, p_cut, p_fail

@p_prolog(guard=lambda data, item: item in data)
def find_path(data, item):
    # Clause 1: Direct hit
    p_check(item == 5, "This path only finds 5 directly.")
    print(f"Found {item} directly via Clause 1.")
    yield item

@p_prolog()
def find_path(data, item):
    # Clause 2: Search in nested list
    if isinstance(data, list):
        for index, element in enumerate(data):
            if element == item:
                print(f"Found {item} at index {index} in Clause 2.")
                yield (item, index)
            elif isinstance(element, list):
                # Recursively call find_path for nested lists
                # Note: yield from is a more Pythonic way for generator delegation
                for res in find_path(element, item):
                    print(f"Found {item} in nested list via Clause 2.")
                    yield res

@p_prolog()
def find_path(data, item):
    # Clause 3: Fallback for any other case (no specific guard)
    print(f"Item {item} not found in specific ways, checking general.")
    p_check(item > 10, "Fallback only works for items greater than 10.")
    yield f"Fallback solution for {item}"

print("--- Searching for 5 ---")
# Only Clause 1's guard will pass, it yields 5, and the predicate succeeds.
# No cut, so all clauses could theoretically run if 5 wasn't found directly.
print(find_path([1, 2, 5, 8], 5))
# Expected output:
# Found 5 directly via Clause 1.
# [5]

print("\n--- Searching for 8 (no direct hit, found in list) ---")
print(find_path([1, 2, 5, 8], 8))
# Expected output:
# Item 8 not found in specific ways, checking general. (Clause 1 guard fails, Clause 2 iterates)
# Found 8 at index 3 in Clause 2.
# [ (8, 3) ]

print("\n--- Searching for 3 in a nested list ---")
print(find_path([1, [2, 3], 4], 3))
# Expected output:
# Item 3 not found in specific ways, checking general. (Clause 1 guard fails, Clause 2 iterates)
# Found 3 in nested list via Clause 2.
# [(3, 1)]

print("\n--- Searching for 15 (fallback) ---")
print(find_path([1, 2], 15))
# Expected output:
# Item 15 not found in specific ways, checking general.
# ['Fallback solution for 15']

print("\n--- Searching for 1 (fallback fails check) ---")
print(find_path([10], 1))
# Expected output:
# Item 1 not found in specific ways, checking general.
# []
```

Here are other examples with the use of `p_cut`. These are a little bit more diffcult to assess. Basically, what we do here is that when a solution has been found, _we do not engage with the next clause._

`yield` is used with `p_cut()` or any value with want to return.

```python
# Example with p_cut
@p_prolog()
def find_first_positive_even(numbers):
    for n in numbers:
        if n > 0 and n % 2 == 0:
            print(f"Yielding first positive even: {n}")
            yield n
            yield p_cut() # Cut! No further clauses will be checked.
            # This part of the code *after* yield p_cut() still runs for *this* clause.
            print("After cut in first clause.")
            # If there were more yields here, they would still be collected.
        else:
            p_fail() # This makes the current iteration fail and backtrack within the clause

@p_prolog()
def find_first_positive_even(numbers):
    print("Trying second clause for positive even.")
    for n in numbers:
        if n > 0 and n % 2 == 0:
            yield n
            print(f"Yielding from second clause: {n}")


print("\n--- Testing p_cut ---")
# Example: [1, 2, 3, 4]
# - Clause 1:
#   - n=1: p_fail()
#   - n=2: yields 2, yields p_cut(). "After cut in first clause." is printed.
#   - The outer loop for clauses will now *stop* looking for more clauses after this one.
#   - Even if the first clause generator had more yields, they would be collected.
# - Clause 2 will *not* be tried because of the cut from Clause 1.
print(find_first_positive_even([2, 3, 4]))
# Expected output:
# Yielding first positive even: 2
# After cut in first clause.
# [2]

print("\n--- Testing p_cut with no initial match in first clause ---")
# Example: [1, 3, 5, 2]
# - Clause 1:
#   - n=1: p_fail()
#   - n=3: p_fail()
#   - n=5: p_fail()
#   - n=2: yields 2, yields p_cut(). "After cut in first clause."
# - Clause 2 will *not* be tried because of the cut from Clause 1.
print(find_first_positive_even([1, 3, 5, 2]))
# Expected output:
# Yielding first positive even: 2
# After cut in first clause.
# [2]
```

We can contrast the above example with this one, where we test both functions. We can see on this example, that both functions are used to provide the final answer. The values in the second function are multiplied by 10 to distinguish, which function provided a value.

```python
print("\n--- Testing p_cut when first clause never yields p_cut ---")
@p_prolog()
def find_all_odd_numbers(numbers):
    for n in numbers:
        if n % 2 != 0:
            yield n

@p_prolog()
def find_all_odd_numbers(numbers):
    print("Trying second clause for odd numbers.")
    for n in numbers:
        if n % 2 != 0:
            yield n * 10 # Yield a different value to distinguish

print(find_all_odd_numbers([1, 2, 3, 4]))
# Expected output:
# [1, 3, 10, 30] (Order might vary depending on how generator is consumed, but both clauses contribute)
# Trying second clause for odd numbers.
# [1, 3, 10, 30]

# Return Value: Returns a list containing all solutions yielded by successful clauses. 
# An empty list is returned if no solutions are found.
```


## License

BSD 3-Clause License

```
Predicates in Python
Copyright (c) 2025-present Claude ROUX

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions 
are met:

1. Redistributions of source code must retain the above copyright 
notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright 
notice, this list of conditions and the following disclaimer in the 
documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its 
contributors may be used to endorse or promote products derived from 
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE.
```
