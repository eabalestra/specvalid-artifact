-- Accuracy checker for likely invariants produced by SpecFuzzer and add-ons
-- Case study: ListComp02
-- Method under analysis: insert_r

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
    r: (R+Null)     -- argument of insert_r
}

---------------------------------
-- Frame conditions
---------------------------------

-- insert_r does NOT modify _var50
fact {
    SK.s._var50 = SK.s1._var50
}

---------------------------------
-- Ground truth postconditions
---------------------------------

-- 1) The inserted element r is in the list after insert_r
pred groundTruth1[] {
    SK.r in SK.s1._var49
}

-- 2) All previous elements remain in the list (monotonic growth)
pred groundTruth2[] {
    SK.s._var49 in SK.s1._var49
}

-- 3) No removal: the list only grows by at most r
-- (optional but precise)
pred groundTruth3[] {
    SK.s1._var49 = SK.s._var49 + SK.r
}

