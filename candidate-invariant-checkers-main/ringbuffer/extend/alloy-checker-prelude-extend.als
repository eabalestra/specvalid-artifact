-- Accuracy checker for likely invariants produced by SpecFuzzer and add-ons, for the RingBuffer case study.
-- This checker is for the extend method.

-- enable Int arithmetic (add/sub) in predicates
open util/integer

-- sentinel value representing null in the array
one sig Null { }

-- abstract element type stored in the buffer
sig Elem { } 

-- ring buffer state
sig RingBuffer { 
    -- array slots indexed by Int
    data: Int -> lone (Elem + Null),
    -- data.size() in Java
    size: Int,
    -- index of first element in the logical queue
    start: Int,
    -- index of next free position
    free: Int,
    -- logical capacity (number of elements)
    capacity_: Int
}

-- Skolem constants for pre and post state variables (pre ringbuffer rb and post ringbuffer rb1)
one sig SK {
    rb: RingBuffer,
    rb1: RingBuffer,
    -- element being added
    a_value: Elem + Null
}

-- array length = capacity + dummy slot
fun dataCount[s: RingBuffer]: Int { add[s.capacity_, 1] }

-- Facts on Java arrays, regarding size and array definitions
-- (arrays are partial functions with domain 0..size-1)
-- array shape and dummy slot facts
fact {
    -- dummy position at index 0
    all s: RingBuffer | s.data[0] = Null
    -- capacity must be positive
    all s: RingBuffer | s.capacity_ >= 1 
    -- array has at least the dummy slot
    all s: RingBuffer | s.size >= 1
    -- no cells beyond upper bound
    all s: RingBuffer | all i: Int | i >= s.size implies no s.data[i]
    -- no negative indices
    all s: RingBuffer | all i: Int | i < 0 implies no s.data[i]
    -- defined within bounds
    all s: RingBuffer | all i: Int | i >= 0 and i < s.size implies some s.data[i]
}

-- RingBuffer class invariants for circular indexing
-- index ranges for start/free
fact {
    -- start in [1..capacity+1]
    all s: RingBuffer | s.start >= 1 and s.start <= dataCount[s]
    -- free in [1..capacity+1]
    all s: RingBuffer | s.free >= 1 and s.free <= dataCount[s]
    -- indices within array bounds
    all s: RingBuffer | s.start <= s.size and s.free <= s.size
}

-- empty iff start equals free
pred isEmpty[s: RingBuffer] { s.start = s.free }

-- full iff free is just behind start (with wrap)
pred isFull[s: RingBuffer] {
    -- wrap-around case
    (s.start = 1 and s.free = dataCount[s])
    or
    -- linear case
    (s.start > 1 and s.free = sub[s.start, 1])
}

-- index i is in the logical queue segment
pred inSegment[s: RingBuffer, i: Int] {
    -- only real slots (exclude dummy at 0)
    i >= 1 and i <= dataCount[s]
    and
    (
        -- no wrap: [start, free)
        (s.start < s.free and i >= s.start and i < s.free)
        or
        -- wrap: [start..end] U [1..free)
        (s.start > s.free and (i >= s.start or i < s.free))
    )
}

-- extend preserves start/capacity and keeps existing data slots unchanged
pred groundTruth1[] {
    SK.rb1.start = SK.rb.start
    and SK.rb1.capacity_ = SK.rb.capacity_
    and (all i: Int | i >= 0 and i < SK.rb.size implies SK.rb1.data[i] = SK.rb.data[i])
}

-- extend appends one element to the underlying ArrayList
pred groundTruth2[] {
    SK.rb1.size = add[SK.rb.size, 1]
}

-- free advances with wrap-around using dataCount
pred groundTruth3[] {
    (SK.rb.free = dataCount[SK.rb]) implies (SK.rb1.free = 1)
    and
    (SK.rb.free != dataCount[SK.rb]) implies (SK.rb1.free = add[SK.rb.free, 1])
}

-- extend writes the new element at the free index
pred groundTruth4[] {
    SK.rb1.data[SK.rb.free] = SK.a_value
}
