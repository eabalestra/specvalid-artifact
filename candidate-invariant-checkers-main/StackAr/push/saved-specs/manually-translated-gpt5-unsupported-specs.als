-- These are unsupported by translator. Manually specified in Alloy

-- this.topOfStack >= 0
pred fuzzedInv10001[] {
    SK.s1.top >= 0
}

pred checkValidityFuzzedInv10001 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10001[]
}

run checkValidityFuzzedInv10001

-- this.topOfStack >= -1
pred fuzzedInv10002[] {
    SK.s1.top >= -1
}

pred checkValidityFuzzedInv10002 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10002[]
}

run checkValidityFuzzedInv10002

-- this.topOfStack <= daikon.Quant.size(this.theArray)-1
pred fuzzedInv10003[] {
    SK.s1.top <= SK.s1.size - 1
}

pred checkValidityFuzzedInv10003 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10003[]
}

run checkValidityFuzzedInv10003

-- this.topOfStack - \old(this.topOfStack) - 1 == 0
pred fuzzedInv10004[] {
    SK.s1.top - SK.s.top - 1 = 0 
}

pred checkValidityFuzzedInv10004 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10004[]
}

run checkValidityFuzzedInv10004

-- this.theArray.getClass().getName() == java.lang.Object[].class.getName()
pred fuzzedInv10005[] {
    -- trivial because of how arrays are represented. Using type of array instead
    SK.s1.arr in Int -> lone (Elem + Null)
}

pred checkValidityFuzzedInv10005 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10005[]
}

run checkValidityFuzzedInv10005

-- this.theArray.getClass().getName() != \old(x_object.getClass().getName())
pred fuzzedInv10006[] {
    -- trivially true due to typing in Alloy
    -- (Int -> lone (Elem + Null)) != (Elem)
}

pred checkValidityFuzzedInv10006 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10006[]
}

run checkValidityFuzzedInv10006

-- this.theArray.getClass().getName() != x_object.getClass().getName()
pred fuzzedInv10007[] {
    -- trivially true due to typing in Alloy
    -- (Int -> lone (Elem + Null)) != (Elem)
}

pred checkValidityFuzzedInv10007 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10007[]
}

run checkValidityFuzzedInv10007

-- this.theArray.getClass().getName() == \old(this.theArray.getClass().getName())
pred fuzzedInv10008[] {
    -- trivial because of how arrays are represented. Using type of array instead
    SK.s1.arr in Int -> lone (Elem + Null)
}

pred checkValidityFuzzedInv10008 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10008[]
}

run checkValidityFuzzedInv10008

-- this.theArray == \old(this.theArray). 
pred fuzzedInv10009[] {
	-- Trivially true, but can't be expressed because of the way the
	-- array object is represented in Alloy. Speaking about size instead.
	SK.s1.size = SK.s.size   
}

pred checkValidityFuzzedInv10009 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10009[]
}

run checkValidityFuzzedInv10009

-- this.theArray != null
pred fuzzedInv10010[] {
    -- trivial because of how arrays are represented. Using size instead
	SK.s1.size >= 0
}

pred checkValidityFuzzedInv10010 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10010[]
}

run checkValidityFuzzedInv10010

-- daikon.Quant.size(this.theArray) == \old(daikon.Quant.size(this.theArray))
pred fuzzedInv10011[] {
	SK.s1.size = SK.s.size    
}

pred checkValidityFuzzedInv10011 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10011[]
}

run checkValidityFuzzedInv10011 

-- daikon.Quant.memberOf(\old(x_object.getClass().getName()) , daikon.Quant.typeArray(this.theArray) )
pred fuzzedInv10012[] {
    some n: Int | n >= 0 and n < SK.s1.size and SK.s1.arr[n] in Elem
}

pred checkValidityFuzzedInv10012 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10012[]
}

run checkValidityFuzzedInv10012

-- \old(x_object) == daikon.Quant.getElement_Object(this.theArray, this.topOfStack)
pred fuzzedInv10013[] {
    SK.x = SK.s1.arr[SK.s1.top]
}

pred checkValidityFuzzedInv10013 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10013[]
}

run checkValidityFuzzedInv10013

-- \old(this.topOfStack) < daikon.Quant.size(this.theArray)-1
pred fuzzedInv10014[] {
    SK.s.top < SK.s1.size - 1
}

pred checkValidityFuzzedInv10014 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10014[]
}

run checkValidityFuzzedInv10014

-- \old(daikon.Quant.getElement_Object(this.theArray, \new(this.topOfStack))) == null
pred fuzzedInv10015[] {
    SK.s.arr[SK.s1.top] = Null
}

pred checkValidityFuzzedInv10015 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10015[]
}

run checkValidityFuzzedInv10015

-- FuzzedInvariant ( some n : StackAr.theArray : n = null ) holds for: this
pred fuzzedInv10016[] {
    some n: Int | n >= 0 and n < SK.s1.size and SK.s1.arr[n] = Null
}

pred checkValidityFuzzedInv10016 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10016[]
}

run checkValidityFuzzedInv10016

-- FuzzedInvariant ( Integer_Variable_0 <= #(StackAr.theArray) ) holds for: <orig(this), this.topOfStack>
pred fuzzedInv10017[] {
	SK.s1.top <= SK.s.size    
}

pred checkValidityFuzzedInv10017 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10017[]
}

run checkValidityFuzzedInv10017

-- FuzzedInvariant ( Integer_Variable_0 < #(StackAr.theArray) ) holds for: <orig(this), this.topOfStack>
pred fuzzedInv10018[] {
    SK.s1.top < SK.s.size
}

pred checkValidityFuzzedInv10018 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10018[]
}

run checkValidityFuzzedInv10018

-- FuzzedInvariant ( Integer_Variable_0 != #(StackAr.theArray) ) holds for: <orig(this), this.topOfStack>
pred fuzzedInv10019[] {
    SK.s1.top != SK.s.size
}

pred checkValidityFuzzedInv10019 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not fuzzedInv10019[]
}

run checkValidityFuzzedInv10019

