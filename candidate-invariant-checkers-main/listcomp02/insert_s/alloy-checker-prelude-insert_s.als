-- Accuracy checker for likely invariants produced by SpecFuzzer and add-ons
-- Case study: ListComp02
-- Method under analysis: insert_s

---------------------------------
-- Basic domains
---------------------------------

sig R {
    A: Int,
    B: one String
}

sig S {
    B: one String,
    C: Int
}

one sig Null {}

---------------------------------
-- ListComp02 object
---------------------------------

sig ListComp02 {
    -- models java.util.ArrayList<R>
    _var49: set (R+Null),

    -- models java.util.ArrayList<S>
    _var50: set (S+Null)
}

---------------------------------
-- Skolem constants (pre/post state)
---------------------------------

one sig SK {
    s: ListComp02,   -- pre-state
    s1: ListComp02, -- post-state
    e: (S+Null)     -- argument of insert_s
}

---------------------------------
-- Frame conditions
---------------------------------

-- insert_s does NOT modify _var49
fact {
    SK.s._var49 = SK.s1._var49
}

---------------------------------
-- Ground truth postconditions
---------------------------------

-- 1) The inserted element e is in the list after insert_s
pred groundTruth1[] {
    SK.e in SK.s1._var50
}

-- 2) All previous elements remain in the list (monotonic growth)
pred groundTruth2[] {
    SK.s._var50 in SK.s1._var50
}

-- 3) No removal: the list only grows by at most r
-- (optional but precise)
pred groundTruth3[] {
    SK.s1._var50 = SK.s._var50 + SK.e
}

