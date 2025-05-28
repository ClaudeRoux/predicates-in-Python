"""
PREDICATE Example
Copyright 2025-present NAVER Corp.
The 3-Clause BSD License

This file presents some examples of how to use these predicate decorators
"""

from predicate import *

# Predicate definition 1
@predicate(guard=lambda a, b: isinstance(a, int) and isinstance(b, int))
def numbers_relation(a, b):
    print(f"Attempting numbers_relation clause 1 (int < int) with: {a}, {b}")
    p_check(a < b)
    print(f"{a} est inférieur à {b}. Clause réussit implicitement.")

# Predicate definition 2
@predicate(guard=lambda s1, s2: isinstance(s1, str) and isinstance(s2, str))
def numbers_relation(s1, s2):
    print(f"Attempting numbers_relation clause 2 (str len == str len) with: '{s1}', '{s2}'")
    p_check(len(s1) == len(s2))
    print(f"La longueur de '{s1}' est égale à celle de '{s2}'. Clause réussit implicitement.")

@predicate(guard=lambda a, b: isinstance(a, int) and isinstance(b, int))
def numbers_relation(a, b):
    print(f"Attempting numbers_relation clause 3 (int > int) with: {a}, {b}")
    p_check(a >= b)
    print(f"{a} est supérieur à {b}. Clause réussit implicitement.")

# Predicate definition 3 (défaut)
@predicate()
def numbers_relation(*args):
    print(f"Attempting numbers_relation clause 3 (default) with: {args}")
    p_check(len(args) == 2)
    print(f"Reçu exactement deux arguments non int/str. Clause réussit implicitement.")


@principles(guard=lambda a, b, p: isinstance(a, int) and isinstance(b, int) and isinstance(p, list))
def verif(a, b, p):
    print("On compare:",a,b, "premier principe")
    p_check(a < b)
    p.append(1)
    print("Premier principe acquis")

@principles(guard=lambda a, b, p: isinstance(a, int) and isinstance(b, int) and isinstance(p, list))
def verif(a, b, p):
    print("On compare:",a,b, "second principe")
    p_check( b - a == 2)
    p.append(2)
    print("Second principe acquis")

@principles()
def verif(a, b, p):
    print("On compare:",a,b, "troisème principe")
    p_check( a+b < 100)
    p.append(3)
    print("Troisème principe acquis")


# --- Testing (identique) ---
print("--- Testing numbers_relation avec 'p_check' et succès implicite ---")
print(f"numbers_relation(5, 10): {numbers_relation(5, 10)}")
print("-" * 20)
print(f"numbers_relation(10, 5): {numbers_relation(10, 5)}")
print("-" * 20)
print(f"numbers_relation('abc', 'def'): {numbers_relation('abc', 'def')}")
print("-" * 20)
print(f"numbers_relation('abc', 'de'): {numbers_relation('abc', 'de')}")
print("-" * 20)
print(f"numbers_relation(5, 'hello'): {numbers_relation(5, 'hello')}")
print("-" * 20)
print(f"numbers_relation(1, 2, 3): {numbers_relation(1, 2, 3)}")
print("-" * 20)
print(f"numbers_relation('a'): {numbers_relation('a')}")
print("-" * 20)

p = []
print(verif(10,12, p), p)
p = []
print(verif(12,12,p), p)
p = []
print(verif(10,14,p), p)

# Note : Les fonctions décorées par @p_prolog doivent être des générateurs (utiliser 'yield' pour produire des solutions).
# Utilisez check() ou fail() pour les vérifications de conditions à l'intérieur du générateur (elles lèvent PredicateFailed).
# Utilisez yield p_cut() pour signaler une coupe (elle ne lève plus d'exception, mais produit un sentinel).
# L'exécution du corps de la clause continue après yield p_cut().


# --- Exemple d'utilisation pour p_prolog (avec générateurs et yield p_cut) ---

# Un prédicat pour trouver des nombres pairs OU des nombres négatifs dans une liste.
# Chaque clause DOIT ÊTRE UN GÉNÉRATEUR (utiliser yield).
@p_prolog(guard=lambda item, my_list: isinstance(my_list, list))
def find_in_list(item, my_list): # Cette fonction est un générateur
    print(f"  Clause 1: Finding even numbers in {my_list}...")
    # Cette clause réussit et produit 'item' si 'item' est dans la liste ET est pair.
    p_check(item in my_list, f"{item} not found in list")
    p_check(isinstance(item, int) and item % 2 == 0, f"{item} is not an even integer")
    print(f"  Clause 1 succeeded checks for {item}. Yielding {item}.")
    yield item # Produit la solution si tous les checks passent.
    print(f"  Clause 1 continues execution after yielding {item}.") # Cette ligne sera exécutée


@p_prolog(guard=lambda item, my_list: isinstance(my_list, list))
def find_in_list(item, my_list): # Cette fonction est aussi un générateur
    print(f"  Clause 2: Finding negative numbers in {my_list}...")
    # Cette clause réussit et produit 'item' si 'item' est dans la liste ET est négatif.
    p_check(item in my_list, f"{item} not found in list")
    p_check(isinstance(item, (int, float)) and item < 0, f"{item} is not negative")
    print(f"  Clause 2 succeeded checks for {item}. Yielding {item}.")
    yield item # Produit la solution si tous les checks passent.
    # Ajoutons une coupe *après* avoir potentiellement produit la solution
    print(f"  Clause 2 continues execution after yielding {item}. Calling p_cut()...") # Cette ligne sera exécutée
    yield p_cut() # Signale la coupe en produisant le sentinel.
    print(f"  Clause 2 continues execution AFTER p_cut() yield for {item}.") # Cette ligne sera aussi exécutée, mais la coupe arrêtera les clauses SUIVANTES.


# --- Testing p_prolog (avec générateurs et yield p_cut) ---
print("\n--- Testing p_prolog 'find_in_list' (Generators & yield p_cut) ---")

my_list = [1, 2, -3, 4, -5.0, 6]

print(f"find_in_list(4, {my_list}):")
# Expected trace:
#   Clause 1: Guard OK. Body: check OK, check OK. print. Yield 4. Wrapper collects 4. Print after yield. Generator finishes normally.
#   Clause 2: Guard OK. Body: check OK, check FAIL. PredicateFailed raised. Wrapper catches, continues.
# Outer loop ends.
# Result: [4]
print(f"Result: {find_in_list(4, my_list)}")
print("-" * 20)

print(f"find_in_list(-3, {my_list}):")
# Expected trace:
#   Clause 1: Guard OK. Body: check OK, check FAIL. PredicateFailed raised. Wrapper catches, continues.
#   Clause 2: Guard OK. Body: check OK, check OK. print. Yield -3. Wrapper collects -3. Print after yield. Call p_cut(). Yield sentinel. Wrapper identifies sentinel -> cut_encountered = True. Print after p_cut yield. Generator finishes normally.
# Outer loop checks cut flag -> cut_encountered is True -> Break loop.
# Result: [-3] (Correct now because yield happens before yield p_cut)
print(f"Result: {find_in_list(-3, my_list)}")
print("-" * 20)

print(f"find_in_list(-4, {my_list}):")
# Expected trace:
#   Clause 1: Guard OK. Body: check OK, check FAIL. PredicateFailed raised. Wrapper catches, continues.
#   Clause 2: Guard OK. Body: check OK, check FAIL. PredicateFailed raised. Wrapper catches, continues.
# Outer loop ends.
# Result: []
print(f"Result: {find_in_list(-4, my_list)}")
print("-" * 20)

print(f"find_in_list(6.5, {my_list}):")
# Expected trace:
#   Clause 1: Guard OK. Body: check OK, check FAIL. PredicateFailed raised. Wrapper catches, continues.
#   Clause 2: Guard OK. Body: check OK, check FAIL. PredicateFailed raised. Wrapper catches, continues.
# Outer loop ends.
# Result: []
print(f"Result: {find_in_list(6.5, my_list)}")
print("-" * 20)
