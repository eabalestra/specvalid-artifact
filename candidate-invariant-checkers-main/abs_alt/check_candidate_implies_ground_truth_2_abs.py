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
        """Collect all Integer_Variable_* identifiers"""
        self.variables.add('Integer_Variable_Orig_x')
        self.variables.add('Integer_Variable_return')
        self.variables.update(re.findall(r'Integer_Variable_[a-zA-Z0-9_]+', expr))
    
    def _parse_expression(self, expr):
        """Parse and translate an expression with proper operator precedence"""
        expr = expr.strip()
        
        # Remove outer parentheses if they exist and are balanced
        while (expr.startswith('(') and expr.endswith(')') and 
               self._is_balanced(expr[1:-1])):
            expr = expr[1:-1].strip()
        
        # Try to split by logical operators (lowest precedence)
        for op in ["implies", "iff", "xor", "or", "and"]:
            parts = self._split_by_outer_operator(expr, op)
            if parts:
                left = self._parse_expression(parts[0])
                right = self._parse_expression(parts[1])
                smt_op = {
                    "implies": "=>",
                    "iff": "=",
                    "xor": "xor",
                    "or": "or",
                    "and": "and"
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
        if re.fullmatch(r'Integer_Variable_[a-zA-Z0-9_]+', expr):
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
            for var in sorted(self.variables)
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
            return None

        formula = formula_match.group(1).strip()
        variables = [v.strip() for v in formula_match.group(2).split(',')]
    
        # Process variable names
        var_mapping = {}
        for i, var in enumerate(variables):
            # Handle orig(a) -> orig_a
            orig_match = re.match(r'orig\((.*?)\)', var)
            if orig_match:
                var_name = f"Integer_Variable_Orig_{orig_match.group(1)}"
            else:
                var_name = f"Integer_Variable_{var}"
    
            var_mapping[f'Integer_Variable_{i}'] = var_name
    
        # Replace all variables in the formula
        for int_var, mapped_var in var_mapping.items():
            formula = re.sub(r'\b' + re.escape(int_var) + r'\b', mapped_var, formula)
    
        return f"({formula})"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python check_inv_validity_abs.py \"formula\"\n")
        sys.stderr.write("Example: python check_inv_validity_abs.py \"(Integer_Variable_0 = 1)\"\n")
        sys.exit(1)

    translator = SMTLIBTranslator()
    formulas_file = sys.argv[1]
    formulas = list()
    with open(formulas_file) as file:
        for formula in file:
            formulas.append(formula)
    try:
        #ground_truth = "(>= Integer_Variable_return 0)"
        ground_truth = "(or (= Integer_Variable_return Integer_Variable_Orig_x) (= Integer_Variable_return (- Integer_Variable_Orig_x)))"
        print(translator.translate_formula(formulas, ground_truth))
    except ValueError as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

