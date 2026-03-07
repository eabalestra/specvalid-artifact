#!/usr/bin/env python3
import re
import sys


def normalize_operator(op):
    """Translate equality to Alloy syntax."""
    return "=" if op == "==" else op


def normalize_equality(expr):
    """Normalize equality operators in a translated expression."""
    return expr.replace("==", "=")


def translate_assertion(assertion_line, predicate_counter):
    """Try to translate an assertion, return (translation, new_counter) or (None, counter)"""
    assertion_line = assertion_line.strip()
    assertion_line = assertion_line.replace("\\old(", "orig(")
    assertion_line = assertion_line.replace("||", " or ")
    assertion_line = assertion_line.replace("&&", " and ")

    # Pattern 1: Simple Integer_Variable_0 with single field
    match = re.match(
        r"FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*(-?\d+)\s*\)\s+holds for:\s*([^<]+)",
        assertion_line,
    )
    if match:
        operator = normalize_operator(match.group(1))
        value = match.group(2)
        field = match.group(3).strip()

        field_translated = translate_single_field(field)
        if field_translated:
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = (
                f"pred {pred_name}[] {{\n    {field_translated} {operator} {value}\n}}"
            )
            check_pred = create_check_predicate(pred_name)

            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 2: Integer_Variable_0 op Integer_Variable_1 with two fields
    match = re.match(
        r"FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        operator = normalize_operator(match.group(1))
        variables_str = match.group(2)

        variables = [v.strip() for v in variables_str.split(",")]
        if len(variables) == 2:
            var1 = translate_single_field(variables[0])
            var2 = translate_single_field(variables[1])

            if var1 and var2:
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {var1} {operator} {var2}\n}}"
                check_pred = create_check_predicate(pred_name)

                return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 3: Integer_Variable_0 with arithmetic on Integer_Variable_1 and constant
    match = re.match(
        r"FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*([+\-*/%])\s*(-?\d+)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        operator = normalize_operator(match.group(1))
        arith_op = match.group(2)
        value = match.group(3)
        variables_str = match.group(4)

        variables = [v.strip() for v in variables_str.split(",")]
        if len(variables) == 2:
            var1 = translate_single_field(variables[0])
            var2 = translate_single_field(variables[1])

            if var1 and var2:
                arith_func = {
                    "+": "add",
                    "-": "sub",
                    "*": "mul",
                    "/": "div",
                    "%": "rem",
                }.get(arith_op, arith_op)

                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {var1} {operator} {arith_func}[{var2},{value}]\n}}"
                check_pred = create_check_predicate(pred_name)

                return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 4: Integer_Variable_0 op Integer_Variable_1 * Integer_Variable_2 (three variables)
    # FuzzedInvariant ( Integer_Variable_0 != Integer_Variable_1 * Integer_Variable_2 ) holds for: <this.start , orig(this.free) , size(this.data[])>
    match = re.match(
        r"FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*([+\-*/%])\s*Integer_Variable_2\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        operator = normalize_operator(match.group(1))
        arith_op = match.group(2)
        variables_str = match.group(3)

        variables = [v.strip() for v in variables_str.split(",")]
        if len(variables) == 3:
            var0 = translate_single_field(variables[0])
            var1 = translate_single_field(variables[1])
            var2 = translate_single_field(variables[2])

            if var0 and var1 and var2:
                arith_func = {
                    "+": "add",
                    "-": "sub",
                    "*": "mul",
                    "/": "div",
                    "%": "rem",
                }.get(arith_op, arith_op)

                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {var0} {operator} {arith_func}[{var1},{var2}]\n}}"
                check_pred = create_check_predicate(pred_name)

                return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 5: Integer_Variable_0 op Integer_Variable_1 + constant * Integer_Variable_2
    match = re.match(
        r"FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*Integer_Variable_1\s*([+\-*/%])\s*(-?\d+)\s*([+\-*/%])\s*Integer_Variable_2\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        operator = normalize_operator(match.group(1))
        arith_op1 = match.group(2)
        constant = match.group(3)
        arith_op2 = match.group(4)
        variables_str = match.group(5)

        variables = [v.strip() for v in variables_str.split(",")]
        if len(variables) == 3:
            var0 = translate_single_field(variables[0])
            var1 = translate_single_field(variables[1])
            var2 = translate_single_field(variables[2])

            if var0 and var1 and var2:
                arith_func1 = {
                    "+": "add",
                    "-": "sub",
                    "*": "mul",
                    "/": "div",
                    "%": "rem",
                }.get(arith_op1, arith_op1)

                arith_func2 = {
                    "+": "add",
                    "-": "sub",
                    "*": "mul",
                    "/": "div",
                    "%": "rem",
                }.get(arith_op2, arith_op2)

                # Build the expression: var0 operator var1 op1 constant op2 var2
                # For example: Integer_Variable_0 != Integer_Variable_1 + 1 * Integer_Variable_2
                inner_expr = f"{arith_func1}[{var1},{constant}]"
                if arith_op2 == "*":
                    # For multiplication with constant, we need to handle it differently
                    inner_expr = f"{arith_func2}[{constant},{var2}]"
                else:
                    inner_expr = f"{arith_func2}[{inner_expr},{var2}]"

                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = (
                    f"pred {pred_name}[] {{\n    {var0} {operator} {inner_expr}\n}}"
                )
                check_pred = create_check_predicate(pred_name)

                return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 6: OR operation with parentheses
    match = re.match(
        r"FuzzedInvariant\s*\(\s*\((.+)\)\s+or\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)

        return translate_logical_expression(
            left_expr, right_expr, "or", variables_str, predicate_counter
        )

    # Pattern 7: AND operation with parentheses
    match = re.match(
        r"FuzzedInvariant\s*\(\s*\((.+)\)\s+and\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)

        return translate_logical_expression(
            left_expr, right_expr, "and", variables_str, predicate_counter
        )

    # Pattern 8: IMPLIES operation with parentheses
    match = re.match(
        r"FuzzedInvariant\s*\(\s*\((.+)\)\s+implies\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)

        return translate_logical_expression(
            left_expr, right_expr, "implies", variables_str, predicate_counter
        )

    # Pattern 9: IFF operation with parentheses
    match = re.match(
        r"FuzzedInvariant\s*\(\s*\((.+)\)\s+iff\s+\((.+)\)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)

        return translate_logical_expression(
            left_expr, right_expr, "iff", variables_str, predicate_counter
        )

    # Pattern 10: OR operation without parentheses
    match = re.match(
        r"FuzzedInvariant\s*\(\s*(.+)\s+or\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)

        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith("(") and left_expr.endswith(")")):
            left_expr = f"({left_expr})"
        if not (right_expr.startswith("(") and right_expr.endswith(")")):
            right_expr = f"({right_expr})"

        return translate_logical_expression(
            left_expr[1:-1], right_expr[1:-1], "or", variables_str, predicate_counter
        )

    # Pattern 11: AND operation without parentheses
    match = re.match(
        r"FuzzedInvariant\s*\(\s*(.+)\s+and\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)

        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith("(") and left_expr.endswith(")")):
            left_expr = f"({left_expr})"
        if not (right_expr.startswith("(") and right_expr.endswith(")")):
            right_expr = f"({right_expr})"

        return translate_logical_expression(
            left_expr[1:-1], right_expr[1:-1], "and", variables_str, predicate_counter
        )

    # Pattern 12: IMPLIES operation without parentheses
    match = re.match(
        r"FuzzedInvariant\s*\(\s*(.+)\s+implies\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)

        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith("(") and left_expr.endswith(")")):
            left_expr = f"({left_expr})"
        if not (right_expr.startswith("(") and right_expr.endswith(")")):
            right_expr = f"({right_expr})"

        return translate_logical_expression(
            left_expr[1:-1],
            right_expr[1:-1],
            "implies",
            variables_str,
            predicate_counter,
        )

    # Pattern 13: IFF operation without parentheses
    match = re.match(
        r"FuzzedInvariant\s*\(\s*(.+)\s+iff\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)

        # Check if the expressions have parentheses and add them if needed
        if not (left_expr.startswith("(") and left_expr.endswith(")")):
            left_expr = f"({left_expr})"
        if not (right_expr.startswith("(") and right_expr.endswith(")")):
            right_expr = f"({right_expr})"

        return translate_logical_expression(
            left_expr[1:-1], right_expr[1:-1], "iff", variables_str, predicate_counter
        )

    # Pattern 14: XOR operation
    match = re.match(
        r"FuzzedInvariant\s*\(\s*(.+)\s+xor\s+(.+)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        left_expr = match.group(1).strip()
        right_expr = match.group(2).strip()
        variables_str = match.group(3)

        variables = [v.strip() for v in variables_str.split(",")]

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
                    left_translated = re.sub(
                        r"\b" + re.escape(var_name) + r"\b", translated, left_translated
                    )
                    right_translated = re.sub(
                        r"\b" + re.escape(var_name) + r"\b",
                        translated,
                        right_translated,
                    )

                # Now also handle any remaining this. references
                # Determine default state from variables
                has_orig = any("orig(" in v for v in variables)
                default_stack = "SK.rb" if has_orig else "SK.rb1"

                left_translated = left_translated.replace("this.", f"{default_stack}.")
                right_translated = right_translated.replace(
                    "this.", f"{default_stack}."
                )

                # Handle any remaining orig() references
                left_translated = re.sub(
                    r"orig\(([^)]+)\)",
                    lambda m: translate_orig_reference(m.group(1)),
                    left_translated,
                )
                right_translated = re.sub(
                    r"orig\(([^)]+)\)",
                    lambda m: translate_orig_reference(m.group(1)),
                    right_translated,
                )

                left_translated = normalize_equality(left_translated)
                right_translated = normalize_equality(right_translated)

                # Create XOR expression (Alloy doesn't have built-in XOR, so we use logical equivalence)
                xor_expr = f"({left_translated} or {right_translated}) and not ({left_translated} and {right_translated})"

                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = f"pred {pred_name}[] {{\n    {xor_expr}\n}}"
                check_pred = create_check_predicate(pred_name)

                return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 15: disjunction of equalities for result
    match = re.match(
        r"(\\result|result)\s*==\s*-?\d+(\s+or\s+\1\s*==\s*-?\d+)+$",
        assertion_line,
    )
    if match:
        field = match.group(1)
        values = re.findall(r"==\s*(-?\d+)", assertion_line)
        alloy_field = translate_single_field(field)
        if alloy_field and values:
            disjunctions = " or ".join([f"{alloy_field} = {value}" for value in values])
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {disjunctions}\n}}"
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 16: disjunction of daikon.Quant.size(this.data) equalities
    match = re.match(
        r"(daikon\.Quant\.size\((this\.[A-Za-z0-9_]+)\)\s*==\s*\d+)(\s+or\s+daikon\.Quant\.size\(\2\)\s*==\s*\d+)+$",
        assertion_line,
    )
    if match:
        field = match.group(2)
        values = re.findall(
            r"daikon\.Quant\.size\(this\.[A-Za-z0-9_]+\)\s*==\s*(\d+)",
            assertion_line,
        )
        alloy_field = translate_single_field(field)
        if alloy_field and values:
            disjunctions = " or ".join(
                [f"#({alloy_field}) = {value}" for value in values]
            )
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {disjunctions}\n}}"
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 17: disjunction of equalities for the same field
    match = re.match(
        r"(this\.[A-Za-z0-9_]+)\s*==\s*-?\d+(\s+or\s+\1\s*==\s*-?\d+)+$",
        assertion_line,
    )
    if match:
        field = match.group(1)
        values = re.findall(r"==\s*(-?\d+)", assertion_line)
        alloy_field = translate_single_field(field)
        if alloy_field and values:
            disjunctions = " or ".join([f"{alloy_field} = {value}" for value in values])
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {disjunctions}\n}}"
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 16: this.* (=|!=) null
    match = re.match(r"(this\.[A-Za-z0-9_]+)\s*([!=]=)\s*null$", assertion_line)
    if match:
        field = match.group(1)
        operator = normalize_operator(match.group(2))
        alloy_field = translate_single_field(field)
        if alloy_field:
            if field == "this.data":
                exists_expr = "some" if operator == "!=" else "no"
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = (
                    f"pred {pred_name}[] {{\n    {exists_expr} {alloy_field}\n}}"
                )
            else:
                pred_name = f"fuzzedInv{predicate_counter}"
                pred_body = (
                    f"pred {pred_name}[] {{\n    {alloy_field} {operator} Null\n}}"
                )
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 17: this.field == orig(this.field)
    match = re.match(r"(this\.[A-Za-z0-9_]+)\s*==\s*orig\(\1\)$", assertion_line)
    if match:
        field = match.group(1)
        pre = translate_orig_reference(field)
        post = translate_single_field(field)
        if pre and post:
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {post} = {pre}\n}}"
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 18: simple this.field (op) constant
    match = re.match(
        r"(this\.[A-Za-z0-9_]+)\s*(==|!=|>=|<=|>|<)\s*(-?\d+)$",
        assertion_line,
    )
    if match:
        field = match.group(1)
        operator = match.group(2)
        value = match.group(3)
        alloy_field = translate_single_field(field)
        if alloy_field:
            op = "=" if operator == "==" else operator
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {alloy_field} {op} {value}\n}}"
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 19: simple this.field (op) this.field
    match = re.match(
        r"(this\.[A-Za-z0-9_]+)\s*(==|!=|>=|<=|>|<)\s*(this\.[A-Za-z0-9_]+)$",
        assertion_line,
    )
    if match:
        left_field = match.group(1)
        operator = normalize_operator(match.group(2))
        right_field = match.group(3)
        left_translated = translate_single_field(left_field)
        right_translated = translate_single_field(right_field)
        if left_translated and right_translated:
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = (
                f"pred {pred_name}[] {{\n    {left_translated} {operator} {right_translated}\n}}"
            )
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 20: daikon.Quant.memberOf(orig(a_value.getClass().getName()), daikon.Quant.typeArray(this.data))
    match = re.match(
        r"daikon\.Quant\.memberOf\(\s*orig\(a_value\.getClass\(\)\.getName\(\)\)\s*,\s*daikon\.Quant\.typeArray\(this\.data\)\s*\)\s*$",
        assertion_line,
    )
    if match:
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = (
            "pred {name}[] {{\n"
            "    some i: Int | i >= 1 and i < SK.rb1.size and SK.rb1.data[i] = SK.a_value\n"
            "}}"
        ).format(name=pred_name)
        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 21: a_value.getClass().getName() == java.lang.String.class.getName()
    match = re.match(
        r"a_value\.getClass\(\)\.getName\(\)\s*==\s*java\.lang\.String\.class\.getName\(\)\s*$",
        assertion_line,
    )
    if match:
        pred_name = f"fuzzedInv{predicate_counter}"
        pred_body = f"pred {pred_name}[] {{\n    SK.a_value != Null\n}}"
        check_pred = create_check_predicate(pred_name)
        return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 19: quantifiers over RingBuffer.data
    match = re.match(
        r"FuzzedInvariant\s*\(\s*(all|no|some)\s+n\s*:\s*([A-Za-z0-9_]+\.[A-Za-z0-9_]+)\s*:\s*(n\s*(?:=|!=)\s*null)\s*\)\s*holds\s*for:\s*(this|orig\(this\))\s*$",
        assertion_line,
    )
    if match:
        quantifier = match.group(1)
        field = match.group(2)
        condition = match.group(3)
        scope = match.group(4)

        if field.endswith(".data"):
            base = "SK.rb1" if scope == "this" else "SK.rb"
            data_field = f"{base}.data"
            size_field = f"{base}.size"
            op = "!=" if "!=" in condition else "="
            if quantifier in ("some", "no"):
                expr = (
                    f"{quantifier} i: Int | i >= 0 and i < {size_field} and "
                    f"{data_field}[i] {op} Null"
                )
            else:
                expr = (
                    f"all i: Int | i >= 0 and i < {size_field} implies "
                    f"{data_field}[i] {op} Null"
                )
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {expr}\n}}"
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 20: Integer_Variable_0 op #(RingBuffer.data)
    match = re.match(
        r"FuzzedInvariant\s*\(\s*Integer_Variable_0\s*([!=<>]=?)\s*#\(\s*RingBuffer\.data\s*\)\s*\)\s+holds for:\s*<([^>]+)>",
        assertion_line,
    )
    if match:
        operator = normalize_operator(match.group(1))
        variables_str = match.group(2)
        variables = [v.strip() for v in variables_str.split(",")]
        if variables:
            has_pre = any(v.startswith("orig(") and v != "orig(this)" for v in variables)
            data_size = "SK.rb.size" if has_pre else "SK.rb1.size"
            non_object = [v for v in variables if v not in ("this", "orig(this)")]
            if non_object:
                var0 = non_object[0]
                var0_translated = translate_single_field(var0)
                if var0_translated:
                    pred_name = f"fuzzedInv{predicate_counter}"
                    pred_body = f"pred {pred_name}[] {{\n    {var0_translated} {operator} {data_size}\n}}"
                    check_pred = create_check_predicate(pred_name)
                    return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 21: daikon.Quant.size(this.data) (op) n
    match = re.match(
        r"daikon\.Quant\.size\((this\.[A-Za-z0-9_]+)\)\s*(==|>=|>|<|<=|!=)\s*(\d+)$",
        assertion_line,
    )
    if match:
        field = match.group(1)
        op = normalize_operator(match.group(2))
        value = match.group(3)
        alloy_field = translate_single_field(field)
        if alloy_field:
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    #({alloy_field}) {op} {value}\n}}"
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 22: daikon.Quant.pairwiseEqual(this.data, orig(this.data))
    match = re.match(
        r"daikon\.Quant\.pairwiseEqual\((this\.[A-Za-z0-9_]+),\s*orig\(\1\)\)$",
        assertion_line,
    )
    if match:
        field = match.group(1)
        alloy_field = translate_single_field(field)
        old_field = translate_orig_reference(field)
        if alloy_field and old_field:
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {alloy_field} = {old_field}\n}}"
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Pattern 23: daikon.Quant.size(this.data) - 1 == orig(daikon.Quant.size(this.data))
    match = re.match(
        r"daikon\.Quant\.size\((this\.[A-Za-z0-9_]+)\)\s*-\s*1\s*==\s*orig\(daikon\.Quant\.size\(\1\)\)$",
        assertion_line,
    )
    if match:
        field = match.group(1)
        alloy_field = translate_single_field(field)
        old_field = translate_orig_reference(field)
        if alloy_field and old_field:
            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = (
                f"pred {pred_name}[] {{\n    #({alloy_field}) = #({old_field}) + 1\n}}"
            )
            check_pred = create_check_predicate(pred_name)
            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    # Could not translate
    return None, predicate_counter


def translate_logical_expression(
    left_expr, right_expr, operator, variables_str, predicate_counter
):
    """Translate logical expressions (AND/OR/implies/iff) with Integer_Variable references"""
    variables = [v.strip() for v in variables_str.split(",")]

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
                left_translated = re.sub(
                    r"\b" + re.escape(var_name) + r"\b", translated, left_translated
                )
                right_translated = re.sub(
                    r"\b" + re.escape(var_name) + r"\b", translated, right_translated
                )

            # Now also handle any remaining this. references
            # Determine default state from variables
            has_pre = any(v.startswith("orig(") and v != "orig(this)" for v in variables)
            default_stack = "SK.rb" if has_pre else "SK.rb1"

            left_translated = left_translated.replace("this.", f"{default_stack}.")
            right_translated = right_translated.replace("this.", f"{default_stack}.")

            # Handle any remaining orig() references
            left_translated = re.sub(
                r"orig\(([^)]+)\)",
                lambda m: translate_orig_reference(m.group(1)),
                left_translated,
            )
            right_translated = re.sub(
                r"orig\(([^)]+)\)",
                lambda m: translate_orig_reference(m.group(1)),
                right_translated,
            )

            left_translated = normalize_equality(left_translated)
            right_translated = normalize_equality(right_translated)

            # Create the logical expression
            logical_expr = f"({left_translated}) {operator} ({right_translated})"

            pred_name = f"fuzzedInv{predicate_counter}"
            pred_body = f"pred {pred_name}[] {{\n    {logical_expr}\n}}"
            check_pred = create_check_predicate(pred_name)

            return f"{pred_body}\n\n{check_pred}", predicate_counter + 1

    return None, predicate_counter


def translate_single_field(field):
    """Translate a single field reference"""
    field = field.strip()

    if field in ("return", "result", "\\result"):
        return "SK.result"

    if field.startswith("orig(this)."):
        inner = field[len("orig(this).") :]
        if inner == "start":
            return "SK.rb.start"
        elif inner == "free":
            return "SK.rb.free"
        elif inner == "capacity" or inner == "capacity_":
            return "SK.rb.capacity_"
        elif inner == "data":
            return "SK.rb.data"
        else:
            return None

    # Handle size patterns
    if "size(this.data[])" in field:
        if "-1" in field:
            if "orig(" in field:
                return "sub[SK.rb.size,1]"
            else:
                return "sub[SK.rb1.size,1]"
        else:
            if "orig(" in field:
                return "SK.rb.size"
            else:
                return "SK.rb1.size"

    # Handle dataCount() patterns
    if "dataCount" in field:
        if "orig(" in field:
            return "add[SK.rb.capacity_,1]"
        return "add[SK.rb1.capacity_,1]"

    # Handle orig() wrapper
    if field.startswith("orig("):
        inner = field[5:-1]  # Remove 'orig(' and ')'
        if inner == "this.start":
            return "SK.rb.start"
        elif inner == "this.free":
            return "SK.rb.free"
        elif inner in ("this.capacity", "this.capacity_"):
            return "SK.rb.capacity_"
        elif inner == "this.data":
            return "SK.rb.data"
        elif inner == "this":
            return "SK.rb1"
        elif inner == "#(RingBuffer.data)":
            return "SK.rb.size"
        elif inner in ("return", "result", "\\result"):
            return "SK.result"
        else:
            return None

    # Handle regular fields
    if field == "this":
        return "SK.rb1"
    elif field == "a_value":
        return "SK.a_value"
    elif field == "this.data":
        return "SK.rb1.data"
    elif field == "this.start":
        return "SK.rb1.start"
    elif field == "this.free":
        return "SK.rb1.free"
    elif field in ("this.capacity", "this.capacity_"):
        return "SK.rb1.capacity_"
    elif field == "#(RingBuffer.data)":
        return "SK.rb1.size"
    else:
        return None


def translate_orig_reference(inner):
    """Translate an orig(...) reference"""
    if inner == "this":
        return "SK.rb1"
    elif inner == "a_value":
        return "SK.a_value"
    elif inner == "this.start":
        return "SK.rb.start"
    elif inner == "this.free":
        return "SK.rb.free"
    elif inner in ("this.capacity", "this.capacity_"):
        return "SK.rb.capacity_"
    elif inner == "this.data":
        return "SK.rb.data"
    elif "size(this.data[])" in inner:
        if "-1" in inner:
            return "sub[SK.rb.size,1]"
        else:
            return "SK.rb.size"
    elif inner == "#(RingBuffer.data)":
        return "SK.rb.size"
    elif inner in ("return", "result", "\\result"):
        return "SK.result"
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
    skip_prefixes = ("buckets=", "specs=", "===", ":::")
    for line in input_lines:
        if (
            line.startswith(skip_prefixes)
            or line.startswith("DataStructures.")
            or all(ch == "=" for ch in line)
        ):
            continue
        translation, counter = translate_assertion(line, counter)
        if translation:
            generated.append(translation)
        else:
            unsupported.append(line)

    # Write generated predicates
    if generated:
        with open("generated-preds.txt", "w") as f:
            f.write("// Generated by assertion translator\n")
            f.write("// Translated fuzzed invariants to Alloy predicates\n")
            f.write(
                "// Checking against ground truth predicates: groundTruth1, groundTruth2, groundTruth3\n\n"
            )
            for pred in generated:
                f.write(pred + "\n\n")
        print(f"✓ Generated {len(generated)} predicates to generated-preds.txt")

    # Write unsupported specifications
    if unsupported:
        with open("unsupported-candidate-specs.txt", "w") as f:
            for spec in unsupported:
                f.write(spec + "\n")
        print(
            f"✗ Saved {len(unsupported)} unsupported specifications to unsupported-candidate-specs.txt"
        )

    if not generated and not unsupported:
        print("No input found!")


if __name__ == "__main__":
    main()
