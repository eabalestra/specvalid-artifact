import re
import sys


class SMTLIBTranslator:
    def __init__(self):
        self.variables = set()

    def translate_formula(self, formulas, ground_truth):
        """Main entry point for translation"""
        self.variables = set()
        translated = list()
        for formula in formulas:
            formula = SMTLIBTranslator.process_invariant_line(formula)
            self._collect_variables(formula)
            translated.append(self._parse_expression(formula))
        return self._generate_smtlib(translated, ground_truth)
    
    def _collect_variables(self, expr):
        """Collect all Boolean_Variable_* identifiers"""
        self.variables.add('value')
        self.variables.add('trueValue')
        self.variables.add('falseValue')
        self.variables.add('result')
        #self.variables.update(re.findall(r'Boolean_Variable_[a-zA-Z0-9_]+', expr))
        #self.variables.update(re.findall(r'Integer_Variable_[a-zA-Z0-9_]+', expr))
    
    def _parse_expression(self, expr):
        """Parse and translate an expression with proper operator precedence"""
        expr = expr.strip()
        
        # Remove outer parentheses if they exist and are balanced
        while (expr.startswith('(') and expr.endswith(')') and 
               self._is_balanced(expr[1:-1])):
            expr = expr[1:-1].strip()

        # Try to split by unary operator op(...)
        if expr.startswith('!'):
            inner = expr[1:].strip()
            inner_parsed = self._parse_expression(inner)
            return f"(not {inner_parsed})"

        # Try to split by logical operators (lowest precedence)
        for op in ["implies", "iff", "xor", "or", "and", "||"]:
            parts = self._split_by_outer_operator(expr, op)
            if parts:
                left = self._parse_expression(parts[0])
                right = self._parse_expression(parts[1])
                smt_op = {
                    "implies": "=>",
                    "iff": "=",
                    "xor": "xor",
                    "or": "or",
                    "and": "and",
                    "||": "or"
                }[op]
                return f"({smt_op} {left} {right})"
        
        # Try to split by comparison operators
        for op in ["=", "!=", ">", "<", ">=", "<="]:
            parts = self._split_by_outer_operator(expr, op)
            if parts:
                left = self._parse_expression(parts[0])
                right = self._parse_expression(parts[1])
                smt_op = {
                    "=": "=",
                    "!=": "distinct",
                    ">": ">",
                    "<": "<",
                    ">=": ">=",
                    "<=": "<="
                }[op]
                return f"({smt_op} {left} {right})"
        
        # Try to split by arithmetic operators
        for op in ["+", "-", "*", "/", "%"]:
            parts = self._split_by_outer_operator(expr, op)
            if parts:
                left = self._parse_expression(parts[0])
                right = self._parse_expression(parts[1])
                return f"({op} {left} {right})"
        
        # Base cases
        if expr in {"0", "1", "-1", "0.0", "1.0", "-1.0"}:
            return expr
        if expr in {"true", "false"}:
            return expr
        if re.fullmatch(r'Boolean_Variable_[a-zA-Z0-9_]+', expr):
            return expr
        if re.fullmatch(r'Integer_Variable_[a-zA-Z0-9_]+', expr):
            return expr
        if expr in self.variables:
            return expr
        
        raise ValueError(f"Could not parse expression: {expr}")
    
    def _split_by_outer_operator(self, expr, op):
        """Split expression by operator only at the outermost level"""
        depth = 0
        op_len = len(op)
        for i in range(len(expr) - op_len + 1):
            c = expr[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
            elif (depth == 0 and 
                  expr.startswith(op, i) and 
                  (i == 0 or expr[i-1] in ' (') and 
                  (i + op_len == len(expr) or expr[i+op_len] in ' )')):
                left = expr[:i].strip()
                right = expr[i+op_len:].strip()
                return (left, right)
        return None
    
    def _is_balanced(self, expr):
        """Check if parentheses are balanced in the expression"""
        balance = 0
        for c in expr:
            if c == '(':
                balance += 1
            elif c == ')':
                balance -= 1
                if balance < 0:
                    return False
        return balance == 0
    
    def _generate_smtlib(self, translated_exprs, ground_truth_expr):
        """Generate complete SMT-LIB script"""
        declarations = "\n".join(
            f"(declare-const {var} Int)"
            for var in sorted(self.variables) if var != "result"
        )
        declarations += "\n" + "\n".join(
            f"(declare-const {var} Bool)"
            for var in sorted(self.variables) if var == "result"
        )
        result = f"{declarations}\n"
        for translated_expr in translated_exprs:
            result = result + f"(assert {translated_expr})\n"
        result = result + f"(assert (not {ground_truth_expr}))\n"
        result = result + "(check-sat)\n"
        return result

    @staticmethod
    def process_invariant_line(line):
        # Extract the formula part
        formula_match = re.search(r'FuzzedInvariant\s*\((.*?)\)\s*holds for:\s*<(.*?)>', line)
        if not formula_match:
            return process_daikon_line(line)

        formula = formula_match.group(1).strip()
        variables = [v.strip() for v in formula_match.group(2).split(',')]
        # Process variable names
        var_mapping = {}
        for i, var in enumerate(variables):
            # Handle orig(a) -> orig_a
            orig_match = re.match(r'orig\((.*?)\)', var)
            if orig_match:
                var_name = f"Boolean_Variable_Orig_{orig_match.group(1)}"
            else:
                var_name = f"Boolean_Variable_{var}"

            if var == "return":
                var_mapping['Integer_Variable_0'] = "Integer_Variable_return"
            else:
                var_mapping[f'Boolean_Variable_{i}'] = var_name
    
        # Replace all variables in the formula
        for int_var, mapped_var in var_mapping.items():
            formula = re.sub(r'\b' + re.escape(int_var) + r'\b', mapped_var, formula)
    
        return f"({formula})"

def process_daikon_line(line):
    # Directly return the line as formula
    expr = line.strip()
    # replace \old(value) by value
    expr = re.sub(r'\bold\((.*?)\)', r'\1', expr)
    # replace \ by nothing
    expr = expr.replace('\\', '')
    # replace == by =
    expr = expr.replace(' == ', ' = ')
    return expr


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python check_candidate_implies_ground_truth_1_toBoolean.py \"formula\"\n")
        sys.stderr.write("Example: python check_candidate_implies_ground_truth_1_toBoolean.py \"(Boolean_Variable_0 = 1)\"\n")
        sys.exit(1)

    translator = SMTLIBTranslator()
    formulas_file = sys.argv[1]
    formulas = list()
    with open(formulas_file) as file:
        for formula in file:
            formulas.append(formula)
    try:
        ground_truth = "(or (and (= value trueValue) result) (and (= value falseValue) (not result)))"
        print(translator.translate_formula(formulas, ground_truth))
    except ValueError as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

