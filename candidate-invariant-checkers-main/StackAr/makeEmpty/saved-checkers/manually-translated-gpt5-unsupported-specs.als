-- These are unsupported by translator. Manually specified in Alloy

-- this.topOfStack >= -1
pred fuzzedInv10001[] {
	SK.s1.top >= -1
}

pred checkValidityFuzzedInv10001 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv10001[]
}

run checkValidityFuzzedInv10001

-- this.topOfStack == -1 || this.topOfStack == 0 || this.topOfStack == 1
pred fuzzedInv10002[] {
	SK.s1.top = -1 or SK.s1.top = 0 or SK.s1.top = 1
}

pred checkValidityFuzzedInv10002 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv10002[]
}

run checkValidityFuzzedInv10002

-- this.topOfStack == -1
pred fuzzedInv10003[] {
	SK.s1.top = -1   
}

pred checkValidityFuzzedInv10003 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv10003[]
}

run checkValidityFuzzedInv10003

-- this.topOfStack <= daikon.Quant.size(this.theArray)-1
pred fuzzedInv10004[] {
    SK.s1.top <= SK.s1.size - 1
}

pred checkValidityFuzzedInv10004 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv10004[]
}

run checkValidityFuzzedInv10004

-- this.topOfStack <= \old(this.topOfStack)
pred fuzzedInv10005[] {
	SK.s1.top <= SK.s.top    
}

pred checkValidityFuzzedInv10005 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv10005[]
}

run checkValidityFuzzedInv10005

-- this.theArray.getClass().getName() == java.lang.Object[].class.getName()
pred fuzzedInv10006[] {
    -- trivial because of how arrays are represented. Using type of array instead 
	SK.s1.arr in Int -> lone (Elem + Null)
}

pred checkValidityFuzzedInv10006 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv10006[]
}

run checkValidityFuzzedInv10006

-- this.theArray.getClass().getName() == \old(this.theArray.getClass().getName()). 
pred fuzzedInv10007[] {
	-- Trivially true, because of how the pre and post arrays are
	-- represented.
	SK.s1.arr in Int -> lone (Elem + Null)
	SK.s.arr in Int -> lone (Elem + Null)
}

pred checkValidityFuzzedInv10007 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv10007[]
}

run checkValidityFuzzedInv10007

-- this.theArray == \old(this.theArray). 
pred fuzzedInv10008[] {
	-- Trivially true, but can't be expressed because of the way the
	-- array object is represented in Alloy. Speaking about size instead.
	SK.s1.size = SK.s.size   
}

pred checkValidityFuzzedInv10008 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv10008[]
}

run checkValidityFuzzedInv10008

-- this.theArray != null
pred fuzzedInv10009[] {
    -- trivially true. Expressing it via size instead
    SK.s1.size >= 0
}

pred checkValidityFuzzedInv10009 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv10009[]
}

run checkValidityFuzzedInv10009

-- daikon.Quant.size(this.theArray) == \old(daikon.Quant.size(this.theArray))
pred fuzzedInv100010[] {
	SK.s1.size = SK.s.size    
}

pred checkValidityFuzzedInv100010 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv100010[]
}

run checkValidityFuzzedInv100010 

-- daikon.Quant.eltsEqual(this.theArray, null)
pred fuzzedInv100011[] {
	all n: Int | n >= 0 and n < SK.s1.size implies SK.s1.arr[n] = Null    
}

pred checkValidityFuzzedInv100011 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv100011[]
}

run checkValidityFuzzedInv100011 

-- same as previous?
-- daikon.Quant.eltsEqual(daikon.Quant.typeArray(this.theArray), null)
pred fuzzedInv100012[] {
	all n: Int | n >= 0 and n < SK.s1.size implies SK.s1.arr[n] = Null    
}

pred checkValidityFuzzedInv100012 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv100012[]
}

run checkValidityFuzzedInv100012 

-- FuzzedInvariant ( some n : StackAr.theArray : n = null ) holds for: orig(this)
pred fuzzedInv100013[] {
	some n: Int | n >= 0 and n < SK.s1.size and SK.s1.arr[n] = Null    
}

pred checkValidityFuzzedInv100013 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv100013[]
}

run checkValidityFuzzedInv100013

-- FuzzedInvariant ( no n : StackAr.theArray : n != null ) holds for: orig(this)
pred fuzzedInv100014[] {
    no n: Int | n >= 0 and n < SK.s1.size and SK.s1.arr[n] != Null
}

pred checkValidityFuzzedInv100014 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv100014[]
}

run checkValidityFuzzedInv100014

-- FuzzedInvariant ( all n : StackAr.theArray : n = null ) holds for: orig(this)
pred fuzzedInv100015[] {
    all n: Int | n >= 0 and n < SK.s.size implies SK.s1.arr[n] = Null
}

pred checkValidityFuzzedInv100015 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv100015[]
}

run checkValidityFuzzedInv100015

-- FuzzedInvariant ( Integer_Variable_0 <= #(StackAr.theArray) ) holds for: <orig(this), this.topOfStack>
pred fuzzedInv100016[] {
    SK.s1.top <= SK.s.size
}

pred checkValidityFuzzedInv100016 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv100016[]
}

run checkValidityFuzzedInv100016

-- FuzzedInvariant ( Integer_Variable_0 < #(StackAr.theArray) ) holds for: <orig(this), this.topOfStack>
pred fuzzedInv100017[] {
    SK.s1.top < SK.s.size
}

pred checkValidityFuzzedInv100017 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv100017[]
}

run checkValidityFuzzedInv100017

-- FuzzedInvariant ( Integer_Variable_0 != #(StackAr.theArray) ) holds for: <orig(this), this.topOfStack>
pred fuzzedInv100018[] {
    SK.s1.top != SK.s.size
}

pred checkValidityFuzzedInv100018 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv100018[]
}

run checkValidityFuzzedInv100018
