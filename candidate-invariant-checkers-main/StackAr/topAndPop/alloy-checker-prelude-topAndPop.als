-- Accuracy checker for likely invariants produced by SpecFuzzer and add-ons, for the StackAr case study.
-- This checker is for the topAndPop method
one sig Null { }
sig Elem { }
sig StackAr {
    arr: Int -> lone (Elem + Null),
    size: Int,
    top: Int
}
-- Skolem constants for pre and post state variables (pre stack s and post stack s1)
one sig SK {
    s: StackAr,
    s1: StackAr,
    result: Elem + Null
}
-- Facts on Java arrays, regarding size and array definitions 
-- (arrays are partial functions with domain 0..size-1)
fact {
    all s: StackAr | s.size >= 0
    all s: StackAr | all i: Int | i >= s.size implies no s.arr[i]
    all s: StackAr | all i: Int | i < 0 implies no s.arr[i]
    all s: StackAr | all i: Int | i >= 0 and i < s.size implies some s.arr[i]
}
-- Fact regarding array size (array is not changed by the method)
fact {
        SK.s.size = SK.s1.size
}
-- Fact regarding top of pre state stack
fact {
    (SK.s.top >= -1 and SK.s.top < SK.s.size)
}
-- Fact regarding null values over top in array, for precondition state stack
fact {
    all i: Int | i > SK.s.top and i < SK.s.size implies SK.s.arr[i] = Null
}
-- Fact regarding precondition of topAndPop, stack is not empty:
fact {
	SK.s.top >= 0
}

-- stack top is between -1 (empty stack) and array size minus one. 
-- StackAr class invariant. It's redundant since it's implied by postcondition
pred groundTruth1[] {
     SK.s1.top >= -1 and SK.s1.top < SK.s1.size
}
-- top is reduced by one after topAndPop
pred groundTruth2[] {
    SK.s1.top = sub[SK.s.top,1]
}
-- previous top has been set to null after topAndPop
pred groundTruth3[] {
    SK.s1.arr[SK.s.top] = Null
}
-- elements below previous top are unchanged after topAndPop
pred groundTruth4[] {
    all i: Int | i >= 0 and i < SK.s.top implies SK.s1.arr[i] = SK.s.arr[i]
}
-- result is value at position top
pred groundTruth5[] {
    SK.result = SK.s1.arr[SK.s1.top]
}
