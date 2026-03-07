# candidate-invariant-checkers
A collection of scripts and tools to check candidate invariants produced by tools like Daikon and SpecFuzzer, against ground truth invariants

# Description

This collection of scripts can take the output of tools such as Daikon and SpecFuzzer, and for some specific case studies, check their validity against ground truth statements. The scripts may be useful for accuracy analysis of these tools, by automating the validity checking of generated candidate specifications, as well as for checking to what extent the ground truth specifications are covered by the (valid) generated invariants.

The scripts use a combination of Bash and Python, and produce specification checkers against manually provided ground truth statements, using SMT or SAT, via Z3 and Alloy.

# Running a subject
To analyze the invariants for a single subject, for example the `getMin` method,
run the following command:
```bash
./run_subject.sh getMin <candidate_invariants_file>
```
The `<candidate_invariants_file>` must be 
the full path to a text file containing candidate invariants inferred by SpecFuzzer or Daikon.

# Covered case studies

## The getMin() method

This method takes two integer inputs `a` and `b`, and returns the minimum between the two. The ground truth specification corresponds to the method's postcondition, and is composed of three statements:
1. The result is either `a` or `b`
2. The result is smaller or equal to `a`
3. The result is smaller or equal to `b`

These three statements are specified in SMTLIB notation to be checked using Z3, as follows:
1. `(assert (or (= Integer_Variable_return Integer_Variable_Orig_a) (= Integer_Variable_return Integer_Variable_Orig_b)))`
2. `(assert (<= Integer_Variable_return Integer_Variable_Orig_a))`
3. `(assert (<= Integer_Variable_return Integer_Variable_Orig_b))`

The names of the variables have to do with how these variables are referred to in the output of the specification inference tool.

### Scripts

#### Candidate invariant validity check

There are two scripts for checking candidate validity invariance:
- Validity checker generator in Python. The script named `check_inv_validity_getmin.py` receives a candidate postcondition as a command line argument, e.g., `"FuzzedInvariant ( Integer_Variable_0 > Integer_Variable_1 - 1 ) holds for: <orig(a), return>"`, and it performs the following tasks:
    * it parses the formula, looking for variable definitions and performing the replacements as indicated in the `holds for` part of the specification,
    * it generates an SMT formula that defines the variables, asserts the ground truth specifications (all of them), and the negation of the translated candidate postcondition.
    * it checks for satisfiability.
If the formula is satisfiable, the candidate postcondition is invalid. Notice that this script outputs the resulting SMTLIB specification to standard output. An example is the following:
`python check_inv_validity_getmin.py "FuzzedInvariant ( Integer_Variable_0 > Integer_Variable_1 - 1 ) holds for: <orig(a), return>"`
- Validity checker executor in Bash. The script named `check_inv_validity_getmin.sh` receives the name of a text file containing candidate specifications in the above format (one per line), it generates the corresponding validity checker for each of the candidates, and calls Z3 on each candidate. It produces as output two files, one containing the valid invariants (those with unsat outcome), another with the invalid invariants (those with sat outcome). An example of its usage is the following:
`./check_inv_validity_getmin.sh candidate_invariants_getmin.txt`
    The resulting valid invariants would be saved in `valid_candidate_invariants_getmin.txt`, while the invalid ones will be put in `invalid_candidate_invariants_getmin.txt`.

#### Ground truth coverage checkers

In addition to the invariant validity checkers, we also provide scripts to check whether a set of inferred specifications imply the parts of the ground truth. An important assumption is that the ground truth coverage checkers are only run for the *valid* candidates. That is, the user must first check the validity of the invariants, filter out the invalid ones, and for the remaining valid, check which parts of the ground truth are covered. For getMin, we have three scripts:
- `check_candidate_implies_ground_truth_1_getmin.py`: it builds the conjunction of all the provided invariants, adds the negation of the first ground truth assertion, and outputs the corresponding smtlib specification to standard output. A sat result from Z3 on the obtained specification means that the provided invariants fail to cover the corresponding ground truth statement. An unsat outcome means that the provided invariants capture the corresponding part of the ground truth.
- `check_candidate_implies_ground_truth_2_getmin.py`: same as the previous one, but for the second ground truth assertion.
- `check_candidate_implies_ground_truth_3_getmin.py`: same as the previous one, but for the third ground truth assertion.

These scripts directly take the name of the file containing all the valid invariants. An example of its usage is the following:
`python check_candidate_implies_ground_truth_1_getmin.py candidate_invariants_getmin.txt > candidate_checker_1.z3`

A Bash script puts together the three checkers. Its usage is the following:
`./check_candidates_imply_ground_truth_getmin.sh candidate_invariants_getmin.txt`

## The abs() method

This method takes an integer input `x`, and returns its absolute value. Since the method does not state any precondition, its postcondition has to account for MIN_INT. The ground truth is therefore composed of three statements:
1. If `x` is MIN_INT, then the result is also MIN_INT.
2. If `x` is not MIN_INT, then the result is greater or equal than zero. 
3. The result is either `x` or `-x`. 

These three statements are specified in SMTLIB notation to be checked using Z3, as follows:
1. `(assert (or (not (= Integer_Variable_Orig_x -2147483648)) (= Integer_Variable_return -2147483648)))`
2. `(assert (or (= Integer_Variable_Orig_x -2147483648) (>= Integer_Variable_return 0)))`
3. `(assert (or (= Integer_Variable_return Integer_Variable_Orig_x) (= Integer_Variable_return (- Integer_Variable_Orig_x))))`

The names of the variables have to do with how these variables are referred to in the output of the specification inference tool.

### Scripts

Scripts are similar to those provided for getMin().

## The *alternative* abs() method

This case study is essentially the same as the previous method, based on the same code. Its postcondition is, however, simplified, and expressed according to the ground truth postcondition considered in the literature, in previous papers (notable, the SpecFuzzer paper). The ground truth is composed of just two statements:
1. The result is greater or equal to zero. 
2. The result is either `x` or `-x`. 

These three statements are specified in SMTLIB notation to be checked using Z3, as follows:
1. `(assert (>= Integer_Variable_return 0))`
2. `(assert (or (= Integer_Variable_return Integer_Variable_Orig_x) (= Integer_Variable_return (- Integer_Variable_Orig_x))))`


### Scripts

Scripts are similar to those provided for abs() method. These are in a separate directory, `abs_alt`.
