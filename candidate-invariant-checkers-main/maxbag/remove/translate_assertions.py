#!/usr/bin/env python3
import re
import sys

def translate_assertion(assertion_line, predicate_counter):
    """Try to translate an assertion, return (translation, new_counter) or (None, counter)"""

    # Skip unsupported variables
    if "_var1457" in assertion_line or "_var4384" in assertion_line or "_var721" in assertion_line:
        #print(f"-- Skipping unsupported assertion: {assertion_line}")
        return None, predicate_counter

    comment_with_orig_assertion = f"-- {assertion_line}"
    # Pattern 1: Simple Integer_Variable_0 with single field
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*(-?\d+)\s*\)\s+holds for:\s*([^<]+)', assertion_line)
    if match:
        operator = match.group(1)
        value = match.group(2)
        field = match.group(3).strip()
        field_translated = translate_single_field(field)
        if field_translated:
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {field_translated} {operator} {value}\n}}"
            check_pred = create_check_predicate(pred_name)
            
            return f"{comment_with_orig_assertion}\n{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Pattern 2: Integer_Variable_0 op Integer_Variable_1 with two fields
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
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
                
                return f"{comment_with_orig_assertion}\n{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Pattern 3: Integer_Variable_0 with arithmetic on Integer_Variable_1 and constant
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*([+\-*/%])\s*(-?\d+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
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
                
                return f"{comment_with_orig_assertion}\n{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Pattern 4: Integer_Variable_0 op Integer_Variable_1 * Integer_Variable_2 (three variables)
    # FuzzedInvariant ( Integer_Variable_0 != Integer_Variable_1 * Integer_Variable_2 ) holds for: <this.topOfStack , orig(this.topOfStack) , size(this.theArray[])>
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*([+\-*/%])\s*Integer_Variable_2\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
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
                
                return f"{comment_with_orig_assertion}\n{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Pattern 5: Integer_Variable_0 op Integer_Variable_1 + constant * Integer_Variable_2
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*([+\-*/%])\s*(-?\d+)\s*([+\-*/%])\s*Integer_Variable_2\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
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
                
                return f"{comment_with_orig_assertion}\n{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    # Pattern 6: OR operation with parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*\((.+)\)\s+or\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        return translate_logical_expression(left_expr, right_expr, "or", variables_str, predicate_counter, comment_with_orig_assertion)
    
    # Pattern 7: AND operation with parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*\((.+)\)\s+and\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        return translate_logical_expression(left_expr, right_expr, "and", variables_str, predicate_counter, comment_with_orig_assertion)
    
    # Pattern 8: IMPLIES operation with parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*\((.+)\)\s+implies\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        return translate_logical_expression(left_expr, right_expr, "implies", variables_str, predicate_counter, comment_with_orig_assertion)
    
    # Pattern 9: IFF operation with parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*\((.+)\)\s+iff\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        return translate_logical_expression(left_expr, right_expr, "iff", variables_str, predicate_counter, comment_with_orig_assertion)
    
    # Pattern 10: OR operation without parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*(.+)\s+or\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith('(') and left_expr.endswith(')')):
            left_expr = f'({left_expr})'
        if not (right_expr.startswith('(') and right_expr.endswith(')')):
            right_expr = f'({right_expr})'
        
        return translate_logical_expression(left_expr[1:-1], right_expr[1:-1], "or", variables_str, predicate_counter, comment_with_orig_assertion)
    
    # Pattern 11: AND operation without parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*(.+)\s+and\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith('(') and left_expr.endswith(')')):
            left_expr = f'({left_expr})'
        if not (right_expr.startswith('(') and right_expr.endswith(')')):
            right_expr = f'({right_expr})'
        
        return translate_logical_expression(left_expr[1:-1], right_expr[1:-1], "and", variables_str, predicate_counter, comment_with_orig_assertion)
    
    # Pattern 12: IMPLIES operation without parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*(.+)\s+implies\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith('(') and left_expr.endswith(')')):
            left_expr = f'({left_expr})'
        if not (right_expr.startswith('(') and right_expr.endswith(')')):
            right_expr = f'({right_expr})'
        
        return translate_logical_expression(left_expr[1:-1], right_expr[1:-1], "implies", variables_str, predicate_counter, comment_with_orig_assertion)
    
    # Pattern 13: IFF operation without parentheses
    match = re.match(r'FuzzedInvariant\s*\(\s*(.+)\s+iff\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)
        
        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith('(') and left_expr.endswith(')')):
            left_expr = f'({left_expr})'
        if not (right_expr.startswith('(') and right_expr.endswith(')')):
            right_expr = f'({right_expr})'
        
        return translate_logical_expression(left_expr[1:-1], right_expr[1:-1], "iff", variables_str, predicate_counter, comment_with_orig_assertion)
    
    # Pattern 14: XOR operation
    match = re.match(r'FuzzedInvariant\s*\(\s*(.+)\s+xor\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
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
                default_maxbag = "SK.m" if has_orig else "SK.m1"
                
                left_translated = left_translated.replace('this.', f'{default_maxbag}.')
                right_translated = right_translated.replace('this.', f'{default_maxbag}.')
                
                # Handle any remaining orig() references
                left_translated = re.sub(r'orig\(([^)]+)\)', lambda m: translate_orig_reference(m.group(1)), left_translated)
                right_translated = re.sub(r'orig\(([^)]+)\)', lambda m: translate_orig_reference(m.group(1)), right_translated)
                
                # Create XOR expression (Alloy doesn't have built-in XOR, so we use logical equivalence)
                xor_expr = f"({left_translated} or {right_translated}) and not ({left_translated} and {right_translated})"
                
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {xor_expr}\n}}"
                check_pred = create_check_predicate(pred_name)
                
                return f"{comment_with_orig_assertion}\n{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern with quantifiers: FuzzedInvariant ( all|some n : MaxBag._var66253 : n <= Integer_Variable_0 ) holds for: <orig(this), this._var587>
    match = re.match(r'FuzzedInvariant\s*\(\s*(all|some)\s+([^:]+)\s*:\s*MaxBag\._var66253\s*:\s*(.+Integer_Variable_0.+)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        var_name = match.group(1).strip()
        field_name = match.group(2).strip()
        condition = match.group(3).strip()
        variables_str = match.group(4).strip()

        variables = [v.strip() for v in variables_str.split(',')]
        if len(variables) >= 2:
            var0 = translate_single_field(variables[0])
            var1 = translate_single_field(variables[1])

            if var0 and var1:
                # Translate the condition
                condition_translated = condition.replace(f'Integer_Variable_0', var1)

                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {var_name} {field_name}: SK.m1._var66253 | {condition_translated}\n}}"
                check_pred = create_check_predicate(pred_name)

                return f"{comment_with_orig_assertion}\n{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern FuzzedInvariant ( Integer_Variable_0 <= #(MaxBag._var66253) ) holds for: <orig(this), this._var5992>
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*#\(MaxBag\._var66253\)\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        operator = match.group(1)
        variables_str = match.group(2)

        variables = [v.strip() for v in variables_str.split(',')]
        if len(variables) >= 2:
            var0 = translate_single_field(variables[0])
            var1 = translate_single_field(variables[1])
            if var0 and var1:
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {var1} {operator} SK.m1._var66253size\n}}"
                check_pred = create_check_predicate(pred_name)

                return f"{comment_with_orig_assertion}\n{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern FuzzedInvariant ( Integer_Variable_0 in MaxBag._var66253 ) holds for: <orig(this), orig(x)>
    match = re.match(r'FuzzedInvariant\s*\(\s*Integer_Variable_0\s+in\s+MaxBag\._var66253\s*\)\s+holds for:\s*<([^>]+)>', assertion_line)
    if match:
        variables_str = match.group(1)

        variables = [v.strip() for v in variables_str.split(',')]
        if len(variables) >= 2:
            var0 = translate_single_field(variables[0])
            var1 = translate_single_field(variables[1])

            if var0 and var1:
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {var1} in SK.m._var66253\n}}"
                check_pred = create_check_predicate(pred_name)

                return f"{comment_with_orig_assertion}\n{pred_body}\n\n{check_pred}", predicate_counter + 1


    print("----> NO PATTERN MATCHED:", assertion_line)
    # Could not translate
    return None, predicate_counter

def translate_logical_expression(left_expr, right_expr, operator, variables_str, predicate_counter, comment_with_orig_assertion):
    """Translate logical expressions (AND/OR/implies/iff) with Integer_Variable references"""
    variables = [v.strip() for v in variables_str.split(',')]
    print(comment_with_orig_assertion)
    print(variables)
    if len(variables) >= 2:
        # Create mapping from Integer_Variable_N to actual fields
        var_map = {}
        i = 0
        for var in variables:
            var_name = f"Integer_Variable_{i}"
            translated = translate_single_field(var)
            if translated:
                if var == "orig(this)" or var == "this":
                    var_map["MaxBag"] = translated
                else:
                    var_map[var_name] = translated
                    i += 1
        print(var_map)
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
            default_max_bag = "SK.m" if has_orig else "SK.m1"
            
            left_translated = left_translated.replace('this.', f'{default_max_bag}.')
            right_translated = right_translated.replace('this.', f'{default_max_bag}.')
            
            # Handle any remaining orig() references
            left_translated = re.sub(r'orig\(([^)]+)\)', lambda m: translate_orig_reference(m.group(1)), left_translated)
            right_translated = re.sub(r'orig\(([^)]+)\)', lambda m: translate_orig_reference(m.group(1)), right_translated)
            
            # Create the logical expression
            logical_expr = f"({left_translated}) {operator} ({right_translated})"
            print(logical_expr)
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {logical_expr}\n}}"
            check_pred = create_check_predicate(pred_name)
            
            return f"{comment_with_orig_assertion}\n{pred_body}\n\n{check_pred}", predicate_counter + 1
    
    return None, predicate_counter

def translate_single_field(field):
    """Translate a single field reference"""
    field = field.strip()
    
    # Handle size patterns
    if 'size(this._var66253[])' in field:
        if '-1' in field:
            if 'orig(' in field:
                return 'sub[SK.m._var66253size,1]'
            else:
                return 'sub[SK.m1._var66253size,1]'
        else:
            if 'orig(' in field:
                return 'SK.m._var66253size'
            else:
                return 'SK.m1._var66253size'
    
    # Handle orig() wrapper
    if field.startswith('orig('):
        inner = field[5:-1]  # Remove 'orig(' and ')'
        if inner == 'this._var66253':
            return 'SK.m._var66253'
        if inner == 'this._var721':
            return 'SK.m._var721'
        if inner == 'this._var587':
            return 'SK.m._var587'
        if inner == 'this._var5992':
            return 'SK.m._var5992'
        if inner == 'x':
            return 'SK.x'
        elif inner == 'this':
            return 'SK.m'
        else:
            return None
    
    # Handle regular fields
    if field == 'this':
        return 'SK.m1'
    elif field == 'this._var66253':
        return 'SK.m1._var66253'
    elif field == 'this._var721':
        return 'SK.m1._var721'
    elif field == 'this._var587':
        return 'SK.m1._var587'
    elif field == 'this._var5992':
        return 'SK.m1._var5992'
    else:
        return None

def translate_orig_reference(inner):
    """Translate an orig(...) reference"""
    if inner == 'this':
        return 'SK.m'
    elif inner == 'this._var66253':
        return 'SK.m._var66253'
    elif inner == 'this._var721':
        return 'SK.m._var721'
    elif inner == 'this._var587':
        return 'SK.m._var587'
    elif inner == 'this._var5992':
        return 'SK.m._var5992'
    elif 'size(this._var66253[])' in inner:
        if '-1' in inner:
            return 'sub[SK.m._var66253size,1]'
        else:
            return 'SK.m._var66253size'
    elif inner == '#(StackAr.theArray)':
        return 'SK.s.size'
    else:
        return inner

def create_check_predicate(pred_name):
    """Create the validity check predicate"""
    return f"pred checkValidity{pred_name[0].upper() + pred_name[1:]} {{\n    groundTruth1[] and groundTruth2[] and groundTruth3[] and groundTruth4[] and not {pred_name}[]\n}}\n\nrun checkValidity{pred_name[0].upper() + pred_name[1:]}"

def main():
    """Process assertions from stdin"""
    
    # Read all input
    input_lines = [line.strip() for line in sys.stdin if line.strip()]
    
    generated = []
    unsupported = []
    counter = 1
    
    # Process each line
    for line in input_lines:
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
            f.write("// Checking against ground truth predicates: groundTruth1, groundTruth2, groundTruth3, groundTruth4 \n\n")
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
