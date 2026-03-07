-- Accuracy checker for likely invariants produced by SpecFuzzer and add-ons
-- Case study: Map
-- Method under analysis: remove(k)

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
-- Ground truth postconditions for remove(k)
-------------------------------------------------
-- --------------------------------------------
-- GT1: key k is NOT in keys after remove
-- --------------------------------------------
pred groundTruth1[] {
    all i: Int | SK.s1.keys[i] != SK.k
}

-- --------------------------------------------
-- GT2: result is an index where k was before
-- --------------------------------------------
pred groundTruth2[] {
    SK.s.keys[SK.result] = SK.k
}

-- --------------------------------------------
-- GT3: keys and data alignment preserved after remove
-- --------------------------------------------
pred groundTruth3[] {
    all i: Int |
        (some SK.s1.keys[i]) iff (some SK.s1.data[i])
}

-- --------------------------------------------
-- GT4: all keys different from k are preserved
-- --------------------------------------------
pred groundTruth4[] {
    all i: Int |
        SK.s.keys[i] != SK.k implies
            SK.s1.keys[i] = SK.s.keys[i]
}

-- --------------------------------------------
-- GT5: all values different from removed index are preserved
-- --------------------------------------------
pred groundTruth5[] {
    all i: Int |
        SK.s.keys[i] != SK.k implies
            SK.s1.data[i] = SK.s.data[i]
}
