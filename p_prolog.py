"""
p_prolog
Copyright 2025-present NAVER Corp.
The 3-Clause BSD License

Examples of how to use the p_prolog decorator
"""

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
# Then moving to next function
# [5, (5,2)]

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

#-------------------------------------------------------
#-------------------------------------------------------
#-------------------------------------------------------

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
# Example: [1, 3, 2, 7, 9, 5, 4, 11]
# - Clause 1:
#   - n=1: p_fail()
# - Clause 2:
print(find_first_positive_even([1, 3, 2, 7, 9, 5, 4, 11]))
# Expected output:
# Yielding first positive even: 2 and 4
# [2, 4]

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
