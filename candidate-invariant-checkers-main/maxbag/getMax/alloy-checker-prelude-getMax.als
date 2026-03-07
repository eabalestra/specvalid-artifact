-- Accuracy checker for likely invariants produced by SpecFuzzer and add-ons
-- Case study: MaxBag
-- Method under analysis: getMax
open util/boolean

---------------------------------
-- Basic domains
---------------------------------

one sig Null {}

---------------------------------
-- MaxBag object
---------------------------------

sig MaxBag {
    -- models ArrayList<Integer> _var66253;
    _var66253: set Int,
    _var66253size: Int,

    -- models Integer _var5992 (size of the bag)
    _var5992: Int,

    -- models _var587 (maximum value in the bag)
    _var587: Int
}

---------------------------------
-- Skolem constants (pre/post state)
---------------------------------

one sig SK {
    m: MaxBag,   -- pre-state
    m1: MaxBag, -- post-state
    result: Int  -- result of getMax
}

---------------------------------
-- Frame conditions
---------------------------------

fact {
    #(_var66253) = SK.m._var66253size
    SK.m._var66253size >= 0
    SK.m._var66253size = SK.m._var5992
    all n : SK.m._var66253 | n <= SK.m._var587
}

---------------------------------
-- Ground truth postconditions
---------------------------------

-- 1) The returned element is the maximum element in the bag
pred groundTruth1[] {
    SK.result = SK.m._var587
}

-- 2) Bag didn't changed
pred groundTruth2[] {
    SK.m._var66253 = SK.m1._var66253 and SK.m._var66253size = SK.m1._var66253size and SK.m._var5992 = SK.m1._var5992
}

-- 3) Max value didn't change
pred groundTruth3[] {
    SK.m._var587 = SK.m1._var587
}

