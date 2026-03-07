open util/integer

-- -------------------------------
-- Array abstraction
-- -------------------------------
sig ArrayState {
    arr: Int -> lone Int,
	size: Int
}

-- Facts on Java arrays, regarding size and array definitions 
-- (arrays are partial functions with domain 0..size-1)
fact {
    all s: ArrayState | s.size >= 0
    all s: ArrayState | all i: Int | i >= s.size implies no s.arr[i]
    all s: ArrayState | all i: Int | i < 0 implies no s.arr[i]
    all s: ArrayState | all i: Int | i >= 0 and i < s.size implies some s.arr[i]
}

-- -------------------------------
-- State container
-- -------------------------------
one sig SK {
    s: ArrayState,     -- pre-state
    s1: ArrayState,    -- post-state
    ind: Int
}

-- pre and post arrays do not change (only size to refer to it)
fact {
	SK.s.size = SK.s1.size
}

-- ind is a valid array position
fact  {
    SK.ind >= 0
    SK.ind < SK.s.size
}


pred groundTruth1[] {
	-- element at ind is incremented by one
	SK.s1.arr[SK.ind] = add[SK.s.arr[SK.ind], 1]
}

pred groundTruth2[] {
	-- no other element in the array changes (other than ind)
	all i: Int | i >= 0 and i < SK.s.size and i != SK.ind implies SK.s1.arr[i] = SK.s.arr[i]
}

pred show[] { groundTruth1[] and groundTruth2[] }

run show for 4 but exactly 2 ArrayState
