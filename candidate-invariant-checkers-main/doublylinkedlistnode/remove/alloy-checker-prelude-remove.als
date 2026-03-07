sig DoublyLinkedListNode {
    left  : one DoublyLinkedListNode,
    right : one DoublyLinkedListNode
}


one sig SK {
    s  : one DoublyLinkedListNode,  -- this (pre)
    s1 : one DoublyLinkedListNode,  -- this (post)
}

fact bidirectional {
    all x : DoublyLinkedListNode {
        x.left.right = x
        x.right.left = x
    }
}

fact singletonAllowed {
    some x : DoublyLinkedListNode |
        x.left = x and x.right = x
}

fact noNull {
    all x : DoublyLinkedListNode {
        x.left != none
        x.right != none
    }
}


-- --------------------------------------------
-- GT1: node is singleton 
-- --------------------------------------------
pred groundTruth1[] {
    SK.s1.right = SK.s1
    SK.s1.left  = SK.s1
}
