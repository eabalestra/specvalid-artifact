#!/usr/bin/env python3
import re
import sys

def translate_assertion(assertion_line, predicate_counter):
    """Try to translate an assertion, return (translation, new_counter) or (None, counter)"""
    print(f"spec: {assertion_line}")

    # Pattern 1: Simple Integer_Variable_0 with single field
    match = re.match(
        r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*(-?\d+)\s*\)\s+holds for:\s*([^<]+)',
        assertion_line
    )
    if match:
        print("pattern 1")
        operator = match.group(1)
        value = match.group(2)
        field = match.group(3).strip()

        field_translated = translate_single_field(field)
        if field_translated:
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {field_translated} {operator} {value}\n}}"
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Pattern 2: Integer_Variable_0 op Integer_Variable_1 with two fields
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 2")
        operator = match.group(1)
        variables_str = match.group(2)
        
        variables = [v.strip() for v in variables_str.split(',')]
        if len(variables) == 2:
            var1 = translate_single_field(variables[0])
            var2 = translate_single_field(variables[1])
            
            if var1 and var2:
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {var1} {operator} {var2}\n}}"
                check_pred = create_check_predicate(pred_name)
                
                return f"{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Pattern 3: Integer_Variable_0 with arithmetic on Integer_Variable_1 and constant
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*([+\-*/%])\s*(-?\d+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 3")
        operator = match.group(1)
        arith_op = match.group(2)
        value = match.group(3)
        variables_str = match.group(4)
        
        variables = [v.strip() for v in variables_str.split(',')]
        if len(variables) == 2:
            var1 = translate_single_field(variables[0])
            var2 = translate_single_field(variables[1])
            
            if var1 and var2:
                arith_func = {
                    '+': 'add',
                    '-': 'sub',
                    '*': 'mul',
                    '/': 'div',
                    '%': 'rem'
                }.get(arith_op, arith_op)
                
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {var1} {operator} {arith_func}[{var2},{value}]\n}}"
                check_pred = create_check_predicate(pred_name)
                
                return f"{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Pattern 4: Integer_Variable_0 op Integer_Variable_1 * Integer_Variable_2 (three variables)
    # FuzzedInvariant ( Integer_Variable_0 != Integer_Variable_1 * Integer_Variable_2 ) holds for: <this.topOfStack , orig(this.topOfStack) , size(this.theArray[])>
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*([+\-*/%])\s*Integer_Variable_2\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 4")
        operator = match.group(1)
        arith_op = match.group(2)
        variables_str = match.group(3)
        
        variables = [v.strip() for v in variables_str.split(',')]
        if len(variables) == 3:
            var0 = translate_single_field(variables[0])
            var1 = translate_single_field(variables[1])
            var2 = translate_single_field(variables[2])
            
            if var0 and var1 and var2:
                arith_func = {
                    '+': 'add',
                    '-': 'sub',
                    '*': 'mul',
                    '/': 'div',
                    '%': 'rem'
                }.get(arith_op, arith_op)
                
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {var0} {operator} {arith_func}[{var1},{var2}]\n}}"
                check_pred = create_check_predicate(pred_name)
                
                return f"{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Pattern 5: Integer_Variable_0 op Integer_Variable_1 + constant * Integer_Variable_2
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*([+\-*/%])\s*(-?\d+)\s*([+\-*/%])\s*Integer_Variable_2\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 5")
        operator = match.group(1)
        arith_op1 = match.group(2)
        constant = match.group(3)
        arith_op2 = match.group(4)
        variables_str = match.group(5)
        
        variables = [v.strip() for v in variables_str.split(',')]
        if len(variables) == 3:
            var0 = translate_single_field(variables[0])
            var1 = translate_single_field(variables[1])
            var2 = translate_single_field(variables[2])
            
            if var0 and var1 and var2:
                arith_func1 = {
                    '+': 'add',
                    '-': 'sub',
                    '*': 'mul',
                    '/': 'div',
                    '%': 'rem'
                }.get(arith_op1, arith_op1)
                
                arith_func2 = {
                    '+': 'add',
                    '-': 'sub',
                    '*': 'mul',
                    '/': 'div',
                    '%': 'rem'
                }.get(arith_op2, arith_op2)
                
                # Build the expression: var0 operator var1 op1 constant op2 var2
                # For example: Integer_Variable_0 != Integer_Variable_1 + 1 * Integer_Variable_2
                inner_expr = f"{arith_func1}[{var1},{constant}]"
                if arith_op2 == '*':
                    # For multiplication with constant, we need to handle it differently
                    inner_expr = f"{arith_func2}[{constant},{var2}]"
                else:
                    inner_expr = f"{arith_func2}[{inner_expr},{var2}]"
                
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {var0} {operator} {inner_expr}\n}}"
                check_pred = create_check_predicate(pred_name)
                
                return f"{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Pattern 6: OR operation with parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*\((.+)\)\s+or\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 6")
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        return translate_logical_expression(left_expr, right_expr, "or", variables_str, predicate_counter)
    
    # Pattern 7: AND operation with parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*\((.+)\)\s+and\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 7")
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        return translate_logical_expression(left_expr, right_expr, "and", variables_str, predicate_counter)
    
    # Pattern 8: IMPLIES operation with parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*\((.+)\)\s+implies\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 8")
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        return translate_logical_expression(left_expr, right_expr, "implies", variables_str, predicate_counter)
    
    # Pattern 9: IFF operation with parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*\((.+)\)\s+iff\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 9")
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        return translate_logical_expression(left_expr, right_expr, "iff", variables_str, predicate_counter)
    
    # Pattern 10: OR operation without parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*(.+)\s+or\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 10")
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith('(') and left_expr.endswith(')')):
            left_expr = f'({left_expr})'
        if not (right_expr.startswith('(') and right_expr.endswith(')')):
            right_expr = f'({right_expr})'
        
        return translate_logical_expression(left_expr[1:-1], right_expr[1:-1], "or", variables_str, predicate_counter)
    
    # Pattern 11: AND operation without parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*(.+)\s+and\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 11")
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith('(') and left_expr.endswith(')')):
            left_expr = f'({left_expr})'
        if not (right_expr.startswith('(') and right_expr.endswith(')')):
            right_expr = f'({right_expr})'
        
        return translate_logical_expression(left_expr[1:-1], right_expr[1:-1], "and", variables_str, predicate_counter)
    
    # Pattern 12: IMPLIES operation without parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*(.+)\s+implies\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 12")
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith('(') and left_expr.endswith(')')):
            left_expr = f'({left_expr})'
        if not (right_expr.startswith('(') and right_expr.endswith(')')):
            right_expr = f'({right_expr})'
        
        return translate_logical_expression(left_expr[1:-1], right_expr[1:-1], "implies", variables_str, predicate_counter)
    
    # Pattern 13: IFF operation without parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*(.+)\s+iff\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 13")
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith('(') and left_expr.endswith(')')):
            left_expr = f'({left_expr})'
        if not (right_expr.startswith('(') and right_expr.endswith(')')):
            right_expr = f'({right_expr})'
        
        return translate_logical_expression(left_expr[1:-1], right_expr[1:-1], "iff", variables_str, predicate_counter)
    
    # Pattern 14: XOR operation
    match = re.match(r'FuzzedInvariant\s*\(\s*(.+)\s+xor\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        print("pattern 14")
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        variables = [v.strip() for v in variables_str.split(',')]
        
        if len(variables) >= 2:
            # Create mapping from Integer_Variable_N to actual fields
            var_map = {}
            for i, var in enumerate(variables):
                var_name = f"Integer_Variable_{i}"
                translated = translate_single_field(var)
                if translated:
                    var_map[var_name] = translated
            
            if len(var_map) >= 2:  # Need at least 2 variables for XOR
                # Replace Integer_Variable references in both expressions
                left_translated = left_expr
                right_translated = right_expr
                
                for var_name, translated in var_map.items():
                    # Replace whole word matches only
                    left_translated = re.sub(r'\b' + re.escape(var_name) + r'\b', translated, left_translated)
                    right_translated = re.sub(r'\b' + re.escape(var_name) + r'\b', translated, right_translated)
                
                # Now also handle any remaining this. references
                # Determine default state from variables
                has_orig = any('orig(' in v for v in variables)
                default_stack = "SK.s" if has_orig else "SK.s1"
                
                left_translated = left_translated.replace('this.', f'{default_stack}.')
                right_translated = right_translated.replace('this.', f'{default_stack}.')
                
                # Handle any remaining orig() references
                left_translated = re.sub(r'orig\(([^)]+)\)', lambda m: translate_orig_reference(m.group(1)), left_translated)
                right_translated = re.sub(r'orig\(([^)]+)\)', lambda m: translate_orig_reference(m.group(1)), right_translated)
                
                # Create XOR expression (Alloy doesn't have built-in XOR, so we use logical equivalence)
                xor_expr = f"({left_translated} or {right_translated}) and not ({left_translated} and {right_translated})"
                
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {xor_expr}\n}}"
                check_pred = create_check_predicate(pred_name)
                
                return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 15: this.* (=|!=) null
    match = re.match(r'(this\.[A-Za-z0-9_]+)\s*([!=]=)\s*null$', assertion_line)
    if match:
        print("Pattern 15")
        field = match.group(1)       # this._var49
        operator = match.group(2)    # == o !=

        alloy_field = translate_single_field(field)
        pred_name = f"fuzzedInv{predicate_counter}"
        alloy_op = 'some' if '!=' else 'no'
        pred_body = f"""pred {pred_name}[] {{
        {alloy_op} {alloy_field}
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 16: == null
    match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*==\s*null$', assertion_line)
    if match:
        print("Pattern 16")
        field = match.group(1)   # r

        alloy_field = translate_single_field(field)
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
        {alloy_field} = Null
    }}"""
        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 17: this.field == old(this.field)
    match = re.match(r'(this\.[A-Za-z0-9_]+)\s*==\s*\\old\(\1\)$', assertion_line)
    if match:
        print("Pattern 17")
        field = match.group(1)

        pre = translate_orig_reference(field)
        post = translate_single_field(field)

        if pre and post:
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"""pred {pred_name}[] {{
        {post} = {pre}
    }}"""
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 18: all|some|no n : n (=|!=) null
    match = re.match(r'FuzzedInvariant\s*\(\s*(all|no|some)\s+n\s*:\s*([A-Za-z0-9_]+\.[A-Za-z0-9_]+)\s*:\s*n\s*((?:=|!=)\s*null)\s*\)\s*holds\s*for:\s*(this|orig\(this\))\s*$', assertion_line
    )
    if match:
        print("Pattern 18")
        quantifier = match.group(1)      # all | no | some
        field = match.group(2)           # _var49 | _var50
        condition = match.group(3)       # n = null | n != null
        scope = match.group(4)           # this | orig(this)


        field = scope + '.' + '.'.join(field.split('.')[1:])
        field = translate_single_field(field)

        condition = condition.replace('null', 'Null')

        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
        {quantifier} i : Int | {field}[i] {condition}
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 19: daikonQuantSize... = n || = m || ... = p 
    match = re.match(
        r'(daikon\.Quant\.size\((this\.[A-Za-z0-9_]+)\)\s*==\s*\d+)'
        r'(\s*\|\|\s*daikon\.Quant\.size\(\2\)\s*==\s*\d+)+',
        assertion_line)
    if match:
        print("Pattern 19")
        sizes = re.findall(
            r'daikon\.Quant\.size\(this\.[A-Za-z0-9_]+\)\s*==\s*(\d+)',
            assertion_line)
        field = match.group(2)
        alloy_field = translate_single_field(field)

        disjunctions = []
        for size in sizes:
            disjunctions.append(f"#({alloy_field}) = {size}")
        disjunctions = ' or '.join(disjunctions)

        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
        {disjunctions}
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 19.1: daikonQuantSize... (op) n 
    match = re.match(
        r'(daikon\.Quant\.size\((this\.[A-Za-z0-9_]+)\)\s*(==|>=|>|<|<=|!=)\s*(\d+))',
        assertion_line)
    if match:
        print("Pattern 19.1")
        field = match.group(2)
        op = match.group(3)
        value = match.group(4)
        alloy_field = translate_single_field(field)

        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
        #({alloy_field}) {op} {value}
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 20: daikonQuanteltsEqual(..., null)
    match = re.match(
        r'daikon\.Quant\.eltsEqual\((?:daikon\.Quant\.typeArray\()?'
        r'(this\.[A-Za-z0-9_]+)\)?,\s*null\)',
        assertion_line
    )
    if match:
        print("Pattern 20")
        field = match.group(1)
        alloy_field = translate_single_field(field)
        
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
        all n : {alloy_field} | n = Null
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1
        
    # Pattern 21: daikonQuantpairwiseEqual(this, old)
    match = re.match(
        r'daikon\.Quant\.pairwiseEqual\((this\.[A-Za-z0-9_]+),\s*\\old\(\1\)\)',
        assertion_line
    )
    if match:
        print("Pattern 21")
        field = match.group(1)
        alloy_field = translate_single_field(field)
        old_field = translate_orig_reference(field)
        
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
            {alloy_field} = {old_field}
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 22: daikonQuantsize(this) == daikonQuantsize(old) + 1
    match = re.match(
        r'daikon\.Quant\.size\((this\.[A-Za-z0-9_]+)\)\s*-\s*1\s*==\s*'
        r'\\old\(daikon\.Quant\.size\(\1\)\)',
        assertion_line
    )
    if match:
        print("Pattern 22")
        field = match.group(1)
        alloy_field = translate_single_field(field)
        old_field = translate_orig_reference(field)
        
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
            #({alloy_field}) = #({old_field}) + 1
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 23.1: \result == v1 || \result == v2 || ... \result == vn
    match = re.match(r'((\\result)\s*==\s*\d+)(\s*\|\|\s*\2\s*==\s*\d+)+', assertion_line)
    if match:
        print("Pattern 23")
        values = re.findall(
            r'\\result\s*==\s*(\d+)',
            assertion_line)
        field = match.group(2)
        alloy_field = translate_single_field(field)

        disjunctions = []
        for v in values:
            disjunctions.append(f'{alloy_field} = {v}')
        disjunctions = ' or '.join(disjunctions)
        
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
            {disjunctions}
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 23: \result 'op' 'value'
    match = re.match(r'(\\result)\s*([!=<>]=?)\s*([A-Za-z0-9_]+)$', assertion_line)
    if match:
        print("Pattern 23")
        field = match.group(1)
        operator = match.group(2)
        value = match.group(3)
        alloy_field = translate_single_field(field)
        
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
            {alloy_field} {operator} {value}
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 24: FuzzedInvariant ( Integer_Variable_0 <= #(field) ) holds for: <orig(ref), val> 
    match = re.match(
        r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*#\([A-Za-z0-9_]+\.([A-Za-z0-9_]+)\)\s*\)\s+holds for:\s*<\s*orig\(([A-Za-z0-9_]+)\)\s*,\s*([A-Za-z0-9_]+)\s*>$',
        assertion_line
    )
    if match:
        print("Pattern 24")
        operator = match.group(1)
        field = match.group(2)
        ref = match.group(3)
        alloy_field_1 = translate_orig_reference(f'{ref}.{field}')
        alloy_field_2 = translate_single_field(match.group(4))
        
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
            #({alloy_field_1}) {operator} {alloy_field_2}
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 25: daikon.Quant.size(this. ... ) {op} \old(daikon.Quant.size(this. ... ))
    match = re.match(
        r'daikon\.Quant\.size\((this\.[A-Za-z0-9_]+)\)\s*([=<>]=?)\s*\\old\(daikon\.Quant\.size\(\1\)\)',
        assertion_line
    )
    if (match):
        print('Pattern 25')
        field = match.group(1)
        operator = match.group(2)
        if operator == '==':
            operator = '='
        alloy_field_1 = translate_single_field(field)
        alloy_field_2 = translate_orig_reference(field)
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
            #({alloy_field_1}) {operator} #({alloy_field_2})
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 25.1: daikon.Quant.size(this. ... )-1 {op} \old(daikon.Quant.size(this. ... ))
    match = re.match(
        r'daikon\.Quant\.size\((this\.[A-Za-z0-9_]+)\)-1\s*([=<>]=?)\s*\\old\(daikon\.Quant\.size\(\1\)\)',
        assertion_line
    )
    if (match):
        print('Pattern 25.1')
        field = match.group(1)
        operator = match.group(2)
        if operator == '==':
            operator = '='
        alloy_field_1 = translate_single_field(field)
        alloy_field_2 = translate_orig_reference(field)
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
            #({alloy_field_1})-1 {operator} #({alloy_field_2})
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 25.2 daikon.Quant.size(this. ... )-1 {op} \old(daikon.Quant.size(this. ... ))-1
    match = re.match(
        r'daikon\.Quant\.size\((this\.[A-Za-z0-9_]+)\)-1\s*([=<>]=?)\s*\\old\(daikon\.Quant\.size\(\1\)\)-1',
        assertion_line
    )
    if (match):
        print('Pattern 25.2')
        field = match.group(1)
        operator = match.group(2)
        if operator == '==':
            operator = '='
        alloy_field_1 = translate_single_field(field)
        alloy_field_2 = translate_orig_reference(field)
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
            #({alloy_field_1})-1 {operator} #({alloy_field_2})-1
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1
        
    # Pattern 26: k != null
    match = re.match(
        r'([A-Za-z0-9_]+)\s*!=\snull',
        assertion_line
    )
    if match:
        print('Pattern 26')
        field = match.group(1)
        alloy_field = translate_single_field(field)
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
            {alloy_field} != Null
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1
        
    # Pattern 27: daikon.Quant.eltsNotEqual(this.data, null)
    match = re.match(
        r'daikon\.Quant\.eltsNotEqual\((this.[A-Za-z0-9_]+),\s*null\)',
        assertion_line
    )
    if match:
        print("Pattern 27")
        field = match.group(1)
        alloy_field = translate_single_field(field)
        
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"""pred {pred_name}[] {{
        no i : Int |{alloy_field}[i] = Null
    }}"""

        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Could not translate
    return None, predicate_counter

def translate_logical_expression(left_expr, right_expr, operator, variables_str, predicate_counter):
    """Translate logical expressions (AND/OR/implies/iff) with Integer_Variable references"""
    variables = [v.strip() for v in variables_str.split(',')]
    
    if len(variables) >= 2:
        # Create mapping from Integer_Variable_N to actual fields
        var_map = {}
        for i, var in enumerate(variables):
            var_name = f"Integer_Variable_{i}"
            translated = translate_single_field(var)
            if translated:
                var_map[var_name] = translated
        
        if len(var_map) >= 2:
            # Replace Integer_Variable references in both expressions
            left_translated = left_expr
            right_translated = right_expr
            
            for var_name, translated in var_map.items():
                # Replace whole word matches only
                left_translated = re.sub(r'\b' + re.escape(var_name) + r'\b', translated, left_translated)
                right_translated = re.sub(r'\b' + re.escape(var_name) + r'\b', translated, right_translated)
            
            # Now also handle any remaining this. references
            # Determine default state from variables
            has_orig = any('orig(' in v for v in variables)
            default_stack = "SK.s" if has_orig else "SK.s1"
            
            left_translated = left_translated.replace('this.', f'{default_stack}.')
            right_translated = right_translated.replace('this.', f'{default_stack}.')
            
            # Handle any remaining orig() references
            left_translated = re.sub(r'orig\(([^)]+)\)', lambda m: translate_orig_reference(m.group(1)), left_translated)
            right_translated = re.sub(r'orig\(([^)]+)\)', lambda m: translate_orig_reference(m.group(1)), right_translated)
            
            # Create the logical expression
            logical_expr = f"({left_translated}) {operator} ({right_translated})"
            
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {logical_expr}\n}}"
            check_pred = create_check_predicate(pred_name)
            
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    return None, predicate_counter

def translate_single_field(field):
    """Translate a single field reference for Map.count"""
    field = field.strip()

    # ------------------------------------------------
    # \result
    # ------------------------------------------------
    if field == r'\result':
        return 'SK.result'

    if field == 'return':
        return 'SK.result'

    if field == 'k':
        return 'SK.k'

    # ------------------------------------------------
    # size(this.keys[])
    # ------------------------------------------------
    if 'size(this.keys[])' in field:
        if '-1' in field:
            if 'orig(' in field:
                return 'sub[SK.s.size,1]'
            else:
                return 'sub[SK.s1.size,1]'
        else:
            if 'orig(' in field:
                return 'SK.s.size'
            else:
                return 'SK.s1.size'

    # ------------------------------------------------
    # size(this.data[])
    # ------------------------------------------------
    if 'size(this.data[])' in field:
        if '-1' in field:
            if 'orig(' in field:
                return 'sub[SK.s.size,1]'
            else:
                return 'sub[SK.s1.size,1]'
        else:
            if 'orig(' in field:
                return 'SK.s.size'
            else:
                return 'SK.s1.size'

    # ------------------------------------------------
    # Direct field access (post-state)
    # ------------------------------------------------
    if field == 'this':
        return 'SK.s1'
    elif field == 'this.keys':
        return 'SK.s1.keys'
    elif field == 'this.data':
        return 'SK.s1.data'
    elif field == 'this.size':
        return 'SK.s1.size'

    # ------------------------------------------------
    # orig(...)
    # ------------------------------------------------
    if field.startswith('orig(this).'):
        inner = field[11:]
        return 'SK.s1.' + inner

    if field.startswith('orig('):
        inner = field[5:-1]

        if inner == 'this':
            return 'SK.s1'
        elif inner == 'this.keys':
            return 'SK.s1.keys'
        elif inner == 'this.data':
            return 'SK.s1.data'
        elif inner == 'this.size':
            return 'SK.s.size'
        elif 'size(this.keys[])' in inner:
            if '-1' in inner:
                return 'sub[SK.s.size,1]'
            else:
                return 'SK.s.size'
        elif 'size(this.data[])' in inner:
            if '-1' in inner:
                return 'sub[SK.s.size,1]'
            else:
                return 'SK.s.size'
        else:
            return None

    return None


def translate_orig_reference(inner):
    """Translate orig(...) references (used inside logical expressions)"""

    if inner == 'this':
        return 'SK.s1'
    elif inner == 'this.keys':
        return 'SK.s1.keys'
    elif inner == 'this.data':
        return 'SK.s1.data'
    elif inner == 'this.size':
        return 'SK.s.size'
    elif 'size(this.keys[])' in inner:
        if '-1' in inner:
            return 'sub[SK.s.size,1]'
        else:
            return 'SK.s.size'
    elif 'size(this.data[])' in inner:
        if '-1' in inner:
            return 'sub[SK.s.size,1]'
        else:
            return 'SK.s.size'

    return inner


# ============================================================
# Alloy boilerplate
# ============================================================
def create_check_predicate(pred_name):
    """Create the validity check predicate"""
    return f"pred checkValidity{pred_name[0].upper() + pred_name[1:]} {{\n    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and groundTruth5[] and not {pred_name}[]\n}}\n\nrun checkValidity{pred_name[0].upper() + pred_name[1:]}"

def main():
    """Process assertions from stdin"""
    
    # Read all input
    input_lines = [line.strip() for line in sys.stdin if line.strip()]
    
    generated = []
    unsupported = []
    counter = 1
    
    # Process each line
    for line in input_lines:
        if '=====' in line or ':::' in line:
            continue
        translation, counter = translate_assertion(line, counter)
        if translation:
            generated.append(translation)
        else:
            unsupported.append(line)
    
    # Write generated predicates
    if generated:
        with open('generated-preds.txt', 'w') as f:
            f.write("// Generated by assertion translator\n")
            f.write("// Translated fuzzed invariants to Alloy predicates\n")
            f.write("// Checking against ground truth predicates: groundTruth1, groundTruth2, groundTruth3\n\n")
            for pred in generated:
                f.write(pred + "\n\n")
        print(f"✓ Generated {len(generated)} predicates to generated-preds.txt")
    
    # Write unsupported specifications
    if unsupported:
        with open('unsupported-candidate-specs.txt', 'w') as f:
            for spec in unsupported:
                f.write(spec + "\n")
        print(f"✗ Saved {len(unsupported)} unsupported specifications to unsupported-candidate-specs.txt")
    
    if not generated and not unsupported:
        print("No input found!")

if __name__ == "__main__":
    main()
