-- Accuracy checker for likely invariants produced by SpecFuzzer and add-ons
-- Case study: Map
-- Method under analysis: extend(k,v)

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
    s: Map,        -- pre-state
    s1: Map,       -- post-state
    k: K,          -- parameter key
    v: V,          -- parameter value
    result: Int    -- returned index
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
-- Ground truth postconditions for extend(k,v)
-------------------------------------------------

-- --------------------------------------------
-- GT1: key k is in keys after extend
-- --------------------------------------------
pred groundTruth1[] {
    some i: Int | SK.s1.keys[i] = SK.k
}

-- --------------------------------------------
-- GT2: value v is in data at same index
-- --------------------------------------------
pred groundTruth2[] {
    SK.s1.data[SK.result] = SK.v
}

-- --------------------------------------------
-- GT3: result is the index of key k
-- --------------------------------------------
pred groundTruth3[] {
    SK.s1.keys[SK.result] = SK.k
}

-- --------------------------------------------
-- GT4: keys and data alignment preserved
-- --------------------------------------------
pred groundTruth4[] {
    all i: Int |
        (some SK.s1.keys[i]) iff (some SK.s1.data[i])
}
