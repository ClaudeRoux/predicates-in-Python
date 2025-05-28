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

