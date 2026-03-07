-- These are unsupported by translator. Manually specified in Alloy

-- this.theArray != null
pred fuzzedInv304DaikonClass1[] {
    -- trivial because of how arrays are represented. Using size instead
	SK.s1.size >= 0
}

pred checkValidityFuzzedInv304DaikonClass1 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv304DaikonClass1[]
}

run checkValidityFuzzedInv304DaikonClass1

-- this.theArray.getClass().getName() == java.lang.Object[].class.getName()
pred fuzzedInv304DaikonClass2[] {
    -- trivial because of how arrays are represented. Using type of array instead 
	SK.s1.arr in Int -> lone (Elem + Null)
}

pred checkValidityFuzzedInv304DaikonClass2 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv304DaikonClass2[]
}

run checkValidityFuzzedInv304DaikonClass2

-- this.topOfStack >= -1
pred fuzzedInv304DaikonClass3[] {
    SK.s1.top >= 1 
}

pred checkValidityFuzzedInv304DaikonClass3 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv304DaikonClass3[]
}

run checkValidityFuzzedInv304DaikonClass3

-- this.topOfStack <= daikon.Quant.size(this.theArray)-1
pred fuzzedInv304DaikonClass4[] {
    SK.s1.top <= SK.s1.size - 1
}

pred checkValidityFuzzedInv304DaikonClass4 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv304DaikonClass4[]
}

run checkValidityFuzzedInv304DaikonClass4

-- this.theArray == \old(this.theArray). 
pred fuzzedInv304pre[] {
	-- Trivially true, but can't be expressed because of the way the
	-- array object is represented in Alloy. Speaking about size instead.
	SK.s1.size = SK.s.size   
}

pred checkValidityFuzzedInv304pre {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv304pre[]
}

run checkValidityFuzzedInv304pre

-- this.theArray.getClass().getName() == \old(this.theArray.getClass().getName()). 
pred fuzzedInv304preBis[] {
	-- Trivially true, because of how the pre and post arrays are
	-- represented.
	SK.s1.arr in Int -> lone (Elem + Null)
	SK.s.arr in Int -> lone (Elem + Null)
}

pred checkValidityFuzzedInv304preBis {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv304preBis[]
}

run checkValidityFuzzedInv304preBis

-- daikon.Quant.size(this.theArray) == \old(daikon.Quant.size(this.theArray))
pred fuzzedInv304[] {
	SK.s1.size = SK.s.size    
}

pred checkValidityFuzzedInv304 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv304[]
}

run checkValidityFuzzedInv304 

-- daikon.Quant.eltsEqual(this.theArray, null)
pred fuzzedInv305[] {
	all n: Int | n >= 0 and n < SK.s1.size implies SK.s1.arr[n] = Null    
}

pred checkValidityFuzzedInv305 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv305[]
}

run checkValidityFuzzedInv305 

-- same as previous?
-- daikon.Quant.eltsEqual(daikon.Quant.typeArray(this.theArray), null)
pred fuzzedInv305pos[] {
	all n: Int | n >= 0 and n < SK.s1.size implies SK.s1.arr[n] = Null    
}

pred checkValidityFuzzedInv305pos {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv305pos[]
}

run checkValidityFuzzedInv305pos 

-- this.topOfStack == -1
pred fuzzedInv306[] {
	SK.s1.top = -1   
}

pred checkValidityFuzzedInv306 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv306[]
}

run checkValidityFuzzedInv306

-- FuzzedInvariant ( all n : StackAr.theArray : n = null ) holds for: orig(this)
pred fuzzedInv307[] {
	all n: Int | n >= 0 and n < SK.s.size implies SK.s1.arr[n] = Null    
}

pred checkValidityFuzzedInv307 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv307[]
}

run checkValidityFuzzedInv307

-- FuzzedInvariant ( no n : StackAr.theArray : n != null ) holds for: orig(this)
pred fuzzedInv308[] {
	no n: Int | n >= 0 and n < SK.s.size and SK.s1.arr[n] != Null    
}

pred checkValidityFuzzedInv308 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv308[]
}

run checkValidityFuzzedInv308

-- FuzzedInvariant ( Integer_Variable_0 != #(StackAr.theArray) ) holds for: <orig(this), this.topOfStack>
pred fuzzedInv309[] {
	SK.s1.top != SK.s.size    
}

pred checkValidityFuzzedInv309 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv309[]
}

run checkValidityFuzzedInv309

-- FuzzedInvariant ( Integer_Variable_0 < #(StackAr.theArray) ) holds for: <orig(this), this.topOfStack>
pred fuzzedInv310[] {
	SK.s1.top < SK.s.size    
}

pred checkValidityFuzzedInv310 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv310[]
}

run checkValidityFuzzedInv310

-- FuzzedInvariant ( Integer_Variable_0 <= #(StackAr.theArray) ) holds for: <orig(this), this.topOfStack>
pred fuzzedInv311[] {
	SK.s1.top <= SK.s.size    
}

pred checkValidityFuzzedInv311 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv311[]
}

run checkValidityFuzzedInv311


-- this.topOfStack <= \old(this.topOfStack)
pred fuzzedInv312[] {
	SK.s1.top <= SK.s.top    
}

pred checkValidityFuzzedInv312 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv312[]
}

run checkValidityFuzzedInv312

-- this.topOfStack < daikon.Quant.size(this.theArray)-1
pred fuzzedInv313[] {
	SK.s1.top <= SK.s1.size - 1    
}

pred checkValidityFuzzedInv313 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv313[]
}

run checkValidityFuzzedInv313

-- \old(this.topOfStack) < daikon.Quant.size(this.theArray)-1
pred fuzzedInv314[] {
	SK.s.top < SK.s1.size - 1    
}

pred checkValidityFuzzedInv314 {
    groundTruth1[] and groundTruth2[] and groundTruth3[] and not fuzzedInv314[]
}

run checkValidityFuzzedInv314

