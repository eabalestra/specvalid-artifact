one sig Null { }

sig DoublyLinkedListNode { }

one sig SK {
	pre_this: one (DoublyLinkedListNode + Null),
	pre_left: DoublyLinkedListNode -> one (DoublyLinkedListNode + Null),
	pre_right: DoublyLinkedListNode -> one (DoublyLinkedListNode + Null),

	post_this:one (DoublyLinkedListNode + Null),
	post_left: DoublyLinkedListNode -> one (DoublyLinkedListNode + Null),
	post_right: DoublyLinkedListNode -> one (DoublyLinkedListNode + Null),

    node_to_insert: one (DoublyLinkedListNode + Null)
}

fact {
	-- pre_this is not null
	SK.pre_this != Null
	-- pre_this is post_this
	SK.pre_this = SK.post_this
	-- pre_left is converse of pre_right
	all n1, n2: DoublyLinkedListNode | (n1 -> n2) in SK.pre_left iff (n2 -> n1) in SK.pre_right
	-- no null in pre_left and pre_right
	all n1: DoublyLinkedListNode | SK.pre_left[n1] != Null and SK.pre_right[n1] != Null
}

fact {
	-- node to insert is not null
	SK.node_to_insert != Null
	-- node to insert is singleton
	SK.pre_left[SK.node_to_insert] = SK.node_to_insert
}

pred groundTruth1[] {
	-- post_left is converse of post_right
	all n1, n2: DoublyLinkedListNode | (n1 -> n2) in SK.post_left iff (n2 -> n1) in SK.post_right
}

pred groundTruth2[] {
	-- left is updated only on the node_to_insert and original right of this
	SK.post_left = SK.pre_left ++ ((SK.node_to_insert -> SK.pre_this) + (SK.pre_this.(SK.pre_right) -> SK.node_to_insert))
}

pred groundTruth3[] {
	-- right is updated only on this and node_to_insert 
	SK.post_right = SK.pre_right ++ ((SK.pre_this -> SK.node_to_insert) + (SK.node_to_insert -> SK.pre_this.(SK.pre_right)))
}

pred groundTruth4[] {
	-- nodes in the list are previous nodes plus inserted node
	SK.post_this.*(SK.post_left) = SK.pre_this.*(SK.pre_left) + SK.node_to_insert
}


pred show[] {
	groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[]
}

run show



