"""
PREDICATE
Copyright 2025-present NAVER Corp.
The 3-Clause BSD License

This file presents three decorators to use Python functions as predicates.
Each predicate function can also be associated with a guard lambda.
"""

import functools

# The registries and exception remain the same
_predicate_registry = {}
_predicate_wrappers = {}

class PredicateFailed(Exception):
    """Custom exception to signal failure within a predicate clause."""
    pass

def p_fail():
    """Helper function to explicitly signal failure within a predicate body."""
    raise PredicateFailed()

def p_check(condition, message=None):
    """
    Performs a boolean check within a predicate clause.
    If the condition is false, signals predicate clause failure
    by raising PredicateFailed.
    """
    if not condition:
        raise PredicateFailed(message)
    # If condition is true, the function simply returns, allowing execution to continue.

def predicate(guard=None):
    """
    Decorator to define a predicate function clause.

    Args:
        guard: An optional function that takes the predicate arguments
               and returns True if this clause should be attempted, False otherwise.
               If None, this clause is attempted if no prior guarded clauses matched.
    """
    def decorator(func):
        pred_name = func.__name__

        if pred_name not in _predicate_registry:
            _predicate_registry[pred_name] = []

            @functools.wraps(func)
            def predicate_wrapper(*args, **kwargs):
                definitions = _predicate_registry.get(pred_name, [])

                for current_guard, pred_func in definitions:
                    try:
                        guard_ok = (current_guard is None) or current_guard(*args, **kwargs)
                    except Exception as e:
                        guard_ok = False

                    if guard_ok:
                        try:
                            # Execute the clause body.
                            # If this line finishes without exception, it's a success for the clause.
                            pred_func(*args, **kwargs)

                            # === Success Branch ===
                            # If we reach here, it means pred_func finished
                            # without raising PredicateFailed. The clause succeeded.
                            return True # Global predicate success (Implicit cut)

                        except PredicateFailed as e:
                            # === Failure Branch ===
                            # The clause explicitly signaled a failure via p_check() or p_fail().
                            # print(f"Clause {pred_func.__name__} for {pred_name} failed: {e}") # Optional debug
                            continue # Move to the next clause (backtracking)

                        except Exception as e:
                             # Handle other unexpected errors.
                             print(f"Unexpected error in predicate clause {pred_name} ({pred_func.__name__}): {e}")
                             continue # Treat as clause failure

                # If the loop finishes, no clause succeeded.
                return False # Global predicate failure.

            _predicate_wrappers[pred_name] = predicate_wrapper

        # Add the clause to the registry (declaration order)
        _predicate_registry[pred_name].append((guard, func))

        # Return the unique wrapper for this name.
        return _predicate_wrappers[pred_name]

    return decorator

# === Registries and Decorator for the AND-like behavior ('principles') ===
_principles_registry = {}
_principles_wrappers = {}

def principles(guard=None):
    """
    Decorator to define a predicate clause for the 'principles' (strict AND) logic.

    For a principles to be True, ALL registered clauses for its name
    (guard AND body) must succeed sequentially. If any guard fails OR any
    body fails after its guard passes, the whole principles is False.

    Args:
        guard: An optional function (args -> bool) determining if this clause
               is applicable. If the guard fails, the entire principles fails.
               If None, the guard always passes.
    """
    def decorator(func):
        pred_name = func.__name__

        # If this predicate name is seen for the first time,
        # initialize its registry and create the unique wrapper.
        if pred_name not in _principles_registry:
            _principles_registry[pred_name] = []

            # === Creation of the unique wrapper instance for this name ===
            # This wrapper is the function that will actually be called by the user (e.g., is_special_number(...)).
            @functools.wraps(func) # Copies the name, docstring, etc., from the first decorated function
            def principles_wrapper(*args, **kwargs):
                # Access the list of clauses registered for this name (built by successive decorators).
                definitions = _principles_registry.get(pred_name, [])

                # In this strict AND interpretation, we iterate. If the guard OR the body of a clause fails,
                # the entire principles fails immediately.
                for current_guard, pred_func in definitions:
                    # For each clause, check guard THEN body.

                    # 1. Check the Guard (part of the overall condition that must succeed)
                    try:
                        # If guard is None, the guard is considered to always succeed for this part of the global AND.
                        guard_ok = (current_guard is None) or current_guard(*args, **kwargs)
                    except Exception as e:
                        # If evaluating the guard raises an error, it's a failure of this part of the global AND.
                        print(f"Error during guard execution for principles {pred_name} (clause {pred_func.__name__}): {e}")
                        return False # Immediate global failure

                    if not guard_ok:
                        # === Failure based on the GUARD ===
                        # The guard itself returned False. In this strict AND, the entire principles fails.
                        # print(f"Guard failed for principles {pred_name} (clause {pred_func.__name__}). Overall failure.") # Debug
                        return False # Immediate global failure

                    # 2. If the Guard succeeded, check the Body (the other part of the AND for this clause)
                    try:
                        # Execute the clause body. It uses check/fail and raises PredicateFailed on failure.
                        pred_func(*args, **kwargs)
                        # If we reach this line, the guard HAS succeeded AND the body HAS succeeded.
                        # We continue the loop to check the next registered clause.

                    except PredicateFailed as e:
                        # === Failure based on the BODY ===
                        # The body explicitly signaled a failure (via check/fail).
                        # In this strict AND, the entire principles fails.
                        # print(f"Body failed for principles {pred_name} (clause {pred_func.__name__}): {e}. Overall failure.") # Debug
                        return False # Immediate global failure

                    except Exception as e:
                         # An unexpected error in the body of a clause. We treat it as an AND failure.
                         print(f"Unexpected error in principles clause {pred_name} ({pred_func.__name__}): {e}. Overall failure.") # Debug
                         return False # Immediate global failure


                # If the loop finished without any clause (guard OR body) returning False:
                # This means all clauses succeeded their guard AND their body sequentially.
                return True # GLOBAL SUCCESS (the AND of all clauses is TRUE)

            # Register this unique wrapper instance for this predicate name.
            _principles_wrappers[pred_name] = principles_wrapper

        # Add the decorated function and its guard to the list of clauses for this predicate name.
        # Uses append() to store in declaration order (Prolog-like order).
        _principles_registry[pred_name].append((guard, func))

        # The decorator ALWAYS returns the unique wrapper instance for this name.
        # This is what will be assigned to the function name (e.g., is_special_number).
        return _principles_wrappers[pred_name]

    return decorator

# --- NEW: Sentinel value and helper function for the Cut ---
# We no longer need the PredicateCut exception if p_cut does not raise it.
# However, the PredicateFailed exception remains necessary for check/fail failures.

# Unique value to signal the cut during yield
_PREDICATE_CUT_SENTINEL = object()

def p_cut():
    """
    Signals a Prolog-like cut by returning a special sentinel value.
    Must be used as 'yield p_cut()' inside a p_prolog generator.
    Execution continues after the yield in the clause body.
    """
    # print("p_cut() called (returns sentinel)") # Debug
    return _PREDICATE_CUT_SENTINEL

# === Registries and Decorator for Prolog-like behavior ('p_prolog') ===
_p_prolog_registry = {}
_p_prolog_wrappers = {}

def p_prolog(guard=None):
    """
    Decorator for Prolog-like logic using generators. Attempts all clauses,
    collects yielded results, allowing backtracking and cut.
    Decorated functions must be generators (use 'yield').

    Args:
        guard: An optional function (args -> bool) determining if this clause
               is applicable. If the guard fails, this clause is skipped.
               If None, the guard always passes.
    """
    def decorator(func):
        pred_name = func.__name__

        if pred_name not in _p_prolog_registry:
            _p_prolog_registry[pred_name] = []

            @functools.wraps(func) # Wraps the *first* func definition
            def p_prolog_wrapper(*args, **kwargs):
                definitions = _p_prolog_registry.get(pred_name, [])
                solutions = [] # List to collect all produced (yielded) solutions

                cut_encountered = False # Flag to indicate if a cut has been encountered

                # Iterate over ALL registered clauses, unless a cut stops the search earlier.
                for current_clause_index, (current_guard, pred_func) in enumerate(definitions):
                    # If a cut has been encountered in a *previous* clause, stop trying *subsequent* clauses.
                    if cut_encountered:
                         break # Exit the main clause exploration loop

                    # --- Check the Guard of the current clause. ---
                    # The try/except here handles execution errors *within the guard itself*.
                    try:
                        guard_ok = (current_guard is None) or current_guard(*args, **kwargs)
                    except Exception as e:
                        print(f"Error in guard for p_prolog {pred_name} (clause {pred_func.__name__}): {e}")
                        guard_ok = False # An error in the guard makes this clause not applicable

                    # If the guard succeeded (or didn't exist)...
                    if guard_ok:
                        # --- Try to execute the Body of the clause (which must be a generator). ---
                        # The try/except here handles exceptions raised *by the code INSIDE the generator*
                        # (PredicateFailed or any other Exception).
                        try:
                            # Call the decorated function to get the generator object
                            result_generator = pred_func(*args, **kwargs)

                            # Iterate over the values produced (yielded) by this generator.
                            # This inner loop handles the execution and exceptions of the generator.
                            for result in result_generator:
                                # If a special value (sentinel) is produced, it's a cut.
                                if result is _PREDICATE_CUT_SENTINEL:
                                    cut_encountered = True # Set the cut flag
                                    # We do NOT collect the sentinel in the solutions list.
                                    # Generator execution (clause body) continues AFTER the yield p_cut().
                                    # The 'for result in...' loop continues to consume the generator.
                                else:
                                    # If a normal value is produced, it's a solution found by this path.
                                    solutions.append(result) # Collect the solution

                                # If the generator terminates normally (implicit StopIteration),
                                # this means that this clause path has been explored without failure.
                                # If a cut was yielded via yield p_cut(), cut_encountered is True.
                                # The 'for result in result_generator' loop terminates.

                            # If we reach here, the generator finished WITHOUT raising PredicateFailed or another Exception.
                            # If a cut was yielded, cut_encountered is True. The flag is set.
                            # The OUTER loop will check this flag before the next iteration.

                        except PredicateFailed as e:
                            # === Failure Branch (in the Body) ===
                            # A check() or fail() function was called INSIDE the generator.
                            # print(f"Clause {pred_func.__name__} for {pred_name} failed during execution: {e}") # Debug
                            # This exploration path failed. We abandon it.
                            # The 'pass' handles the exception. The OUTER loop continues to the next clause definition.
                            pass # Handles clause failure - continues search with the next clause

                        except Exception as e:
                             # An unexpected error occurred INSIDE the generator.
                             print(f"Unexpected error in p_prolog clause {pred_name} ({pred_func.__name__}): {e}")
                             # We treat it as a failure for this exploration path.
                             # The 'pass' handles the exception, and the OUTER loop continues to the next clause.
                             pass # Handles unexpected error - treated as clause failure

                    # Else (guard_ok is False): The guard did not succeed. This clause is not applicable for these arguments.
                    # Execution simply proceeds to the next clause in the OUTER loop.

                # The OUTER loop terminates either because all clauses have been checked,
                # or because the 'cut_encountered' flag has been set to True.
                # Returns the list of all solutions collected from the exploration paths.
                return solutions

            _p_prolog_wrappers[pred_name] = p_prolog_wrapper # Stores the unique wrapper instance

        # Add the current decorated function and its guard to the list of clauses
        # for this p_prolog predicate name in the registry.
        # Uses append() to store in declaration order (Prolog-like order).
        _p_prolog_registry[pred_name].append((guard, func))

        # The decorator ALWAYS returns the unique wrapper instance for this name.
        # This is what will be assigned to the function name (e.g., find_in_list).
        return _p_prolog_wrappers[pred_name]

    return decorator