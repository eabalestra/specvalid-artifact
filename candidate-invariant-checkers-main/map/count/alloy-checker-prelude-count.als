-- Accuracy checker for likely invariants produced by SpecFuzzer and add-ons
-- Case study: Map
-- Method under analysis: count()

-------------------------------------------------
-- Basic atoms
-------------------------------------------------

one sig Null { }
sig K { }
sig V { }

-------------------------------------------------
-- Map state
-------------------------------------------------

sig Map {
    keys: Int -> lone (K + Null),
    data: Int -> lone (V + Null),
    size: Int
}

-------------------------------------------------
-- Skolem constants: pre and post states + result
-------------------------------------------------

one sig SK {
    s: Map,      -- pre-state
    s1: Map,     -- post-state
    result: Int  -- result of count()
}

-------------------------------------------------
-- Facts about list structure (LinkedList abstraction)
-------------------------------------------------

fact {
    -- size is non-negative
    all m: Map | m.size >= 0

    -- keys domain is exactly 0 .. size-1
    all m: Map | all i: Int |
        (i < 0 or i >= m.size) implies no m.keys[i]

    all m: Map | all i: Int |
        (i < 0 or i >= m.size) implies no m.data[i]

    all m: Map | all i: Int |
        i >= 0 and i < m.size implies some m.keys[i]

    all m: Map | all i: Int |
        i >= 0 and i < m.size implies some m.data[i]
}

-------------------------------------------------
-- Ground truth postconditions for count()
-------------------------------------------------

-- GT1: result equals size of the map
pred groundTruth1[] {
    SK.result = SK.s.size
}

-- GT2: size is unchanged (redundant but explicit)
pred groundTruth2[] {
    SK.s1.size = SK.s.size
}

-- GT3: keys unchanged
pred groundTruth3[] {
    SK.s1.keys = SK.s.keys
}

-- GT4: data unchanged
pred groundTruth4[] {
    SK.s1.data = SK.s.data
}
