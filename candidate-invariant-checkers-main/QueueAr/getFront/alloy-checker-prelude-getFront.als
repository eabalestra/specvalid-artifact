-- Accuracy checker for likely invariants produced by SpecFuzzer and add-ons, for the QueueAr case study.
-- This checker is for the getFront method
one sig Null { }
sig Elem { }
sig QueueAr {
    arr: Int -> lone (Elem + Null),
    size: Int,
    currentSize: Int,
    front: Int,
    back: Int
}
-- Skolem constants for pre and post state variables (pre queue q and post queue q1)
one sig SK {
    q: QueueAr,
    q1: QueueAr
}
-- Facts on Java arrays, regarding size and array definitions 
-- (arrays are partial functions with domain 0..size-1)
fact {
    all q: QueueAr | q.size >= 0
    all q: QueueAr | all i: Int | i >= q.size implies no q.arr[i]
    all q: QueueAr | all i: Int | i < 0 implies no q.arr[i]
    all q: QueueAr | all i: Int | i >= 0 and i < q.size implies some q.arr[i]
}
-- Fact regarding array size (array is not changed by the method)
fact {
        SK.q.size = SK.q1.size
}
-- Fact regarding currentSize of pre state queue
fact {
    (SK.q.currentSize >= 0 and SK.q.currentSize <= SK.q.size)
}
-- Fact regarding front of pre state queue
fact {
    (SK.q.front >= 0 and SK.q.front <= SK.q.size - 1)
}
-- Fact regarding back of pre state queue
fact {
    (SK.q.back >= 0 and SK.q.back <= SK.q.size - 1)
}
-- Fact regarding null values in array, for precondition state queue
fact {
    all i: Int | i < SK.q.front or i > SK.q.back implies SK.q.arr[i] = Null
}
-- queue front, back and currentSize have correct values
-- QueueAr class invariant. It's redundant since it's implied by postcondition
pred groundTruth1[] {
     SK.q1.front >= 0 and SK.q1.front <= SK.q1.size - 1 and
     SK.q1.back >= 0 and SK.q1.back <= SK.q1.size - 1 and
     SK.q1.currentSize >= 0 and SK.q1.currentSize <= SK.q1.size
}
-- currentSize did not change after getFront.
pred groundTruth2[] {
    SK.q1.currentSize = SK.q.currentSize
}
-- front did not change after getFront.
pred groundTruth3[] {
    SK.q1.front = SK.q.front
}
-- back did not change after getFront.
pred groundTruth4[] {
    SK.q1.back = SK.q.back
}
-- array did not change after getFront.
pred groundTruth5[] {
    all i: Int | SK.q1.arr[i] = SK.q.arr[i]
}

