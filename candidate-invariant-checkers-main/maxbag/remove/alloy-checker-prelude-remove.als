-- Accuracy checker for likely invariants produced by SpecFuzzer and add-ons
-- Case study: MaxBag
-- Method under analysis: remove
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
    x: Int  -- argument to remove
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

-- 1) The remove element x is not longer in _var66253 after remove
pred groundTruth1[] {
    SK.x not in SK.m1._var66253
}

-- 2) All previous elements remain in the bag except x
pred groundTruth2[] {
    all n : SK.m._var66253 | n != SK.x implies n in SK.m1._var66253
}

-- 3) Max value is correct
pred groundTruth3[] {
    all n : SK.m1._var66253 | n <= SK.m1._var587
}

-- 4) Size decreased by one or the same
pred groundTruth4[] {
    SK.m1._var5992 = SK.m._var5992 - 1 or SK.m1._var5992 = SK.m._var5992
}


