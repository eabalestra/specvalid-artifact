-- Alloy specification of Composite

one sig Null { }

sig Composite { }

one sig SK {
	pre_init_value: Composite -> one Int,
	pre_value: Composite -> one Int,
	pre_children: Composite -> set (Composite + Null),
	pre_parent: Composite -> one (Composite + Null),
	pre_max_child: Composite -> one (Composite + Null),

	pre_this: one (Composite + Null),

	post_init_value: Composite -> one Int,
	post_value: Composite -> one Int,
	post_children: Composite -> set (Composite + Null),
	post_parent: Composite -> one (Composite + Null),
	post_max_child: Composite -> one (Composite + Null),

	post_this: one (Composite + Null),
	
	child_to_add: one (Composite + Null)
}

fact preconditionComposite {
	-- null is not a children
	Null !in SK.pre_children[Composite]
	-- max_child is the maximum of the children
	(all c: Composite | no SK.pre_children[c] implies SK.pre_max_child[c] = Null)
	(all c: Composite | some SK.pre_children[c] implies 
		(SK.pre_max_child[c] != Null and SK.pre_max_child[c] in c.^(SK.pre_children)
		 and (all c1: Composite | c1 in c.^(SK.pre_children) implies SK.pre_value[c1] <= SK.pre_max_child[c].(SK.pre_value))
		)
	)
	-- no composite is its own children
	(all c: Composite | c !in c.^(SK.pre_children))
	-- no composite is its own ancestor
	(all c: Composite | c !in c.^(SK.pre_parent))
	-- child_to_add not null
	SK.child_to_add != Null
	-- child_to_add not already in pre_this children or parent
	SK.child_to_add !in SK.pre_this.^(SK.pre_children)
	SK.child_to_add !in SK.pre_this.^(SK.pre_parent)
	-- child_to_add is not pre_this
	SK.child_to_add != SK.pre_this
	-- pre_this not null
	SK.pre_this != Null
	-- child_to_add has no parent and no children
	SK.pre_parent[SK.child_to_add] = Null
	no SK.pre_children[SK.child_to_add]
	-- pre_this and post_this are the same
	SK.pre_this = SK.post_this
}

pred groundTruth1[] {
	-- children gets updated
	SK.post_children = SK.pre_children + (SK.pre_this -> SK.child_to_add)
}

pred groundTruth2[] {
	-- children satisfies invariant
	(all c: Composite | c !in c.^(SK.post_children))
}

pred groundTruth3[] {
	-- max_child correctly updated
	(all c: Composite | no SK.post_children[c] implies SK.post_max_child[c] = Null)
	(all c: Composite | some SK.post_children[c] implies 
		(SK.post_max_child[c] != Null and SK.post_max_child[c] in c.^(SK.post_children)
		 and (all c1: Composite | c1 in c.^(SK.post_children) implies SK.post_value[c1] <= SK.post_max_child[c].(SK.post_value))
		)
	)	
}
	
pred groundTruth4[] {
	-- value is correctly updated on post_this
	SK.post_value[SK.child_to_add] = SK.pre_value[SK.child_to_add]
	SK.pre_value[SK.child_to_add] > SK.pre_value[SK.pre_this] implies SK.pre_value[SK.child_to_add] = SK.post_value[SK.post_this]
	SK.pre_value[SK.child_to_add] <= SK.pre_value[SK.pre_this] implies SK.pre_value[SK.pre_this] = SK.post_value[SK.post_this]	
}

pred groundTruth5[] {
	-- parent correctly updated
	SK.post_parent = SK.pre_parent ++ (SK.child_to_add -> SK.pre_this)
}

pred groundTruth[] {
	groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and groundTruth5[]
}

run groundTruth
