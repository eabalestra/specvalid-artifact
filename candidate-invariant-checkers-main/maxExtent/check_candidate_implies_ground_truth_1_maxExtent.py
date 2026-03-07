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
        self.variables.add('Double_Variable_maxx')
        self.variables.add('Double_Variable_minx')
        self.variables.add('Double_Variable_maxy')
        self.variables.add('Double_Variable_miny')
        self.variables.add('Double_Variable_return')
        self.variables.update(re.findall(r'Double_Variable_[a-zA-Z0-9_]+', expr))
    
    def _parse_expression(self, expr):
        """Parse and translate an expression with proper operator precedence"""
        expr = expr.strip()

        # replace 'this.' by nothing in expr
        expr = expr.replace('this.', '')

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
        if re.fullmatch(r'Double_Variable_[a-zA-Z0-9_]+', expr):
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
            f"(declare-const {var} Real)"
            for var in sorted(self.variables)
        )
        declarations += "\n(declare-const w Real)"
        declarations += "\n(declare-const h Real)"

        # w = maxx - minx
        # h = maxy - miny
        declarations += f"\n(assert (= (- Double_Variable_maxx Double_Variable_minx) w))"
        declarations += f"\n(assert (= (- Double_Variable_maxy Double_Variable_miny) h))"
        # result == 0 or result == w or result == h
        # (maxx < minx) implies result == 0
        # (maxx >= minx) and w > h implies result = w
        # (maxx >= minx) and w <= h implies result = h
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
                var_name = f"Double_Variable_Orig_{orig_match.group(1)}"
            else:
                var_name = f"Double_Variable_{var}"
    
            var_mapping[f'Double_Variable_{i}'] = var_name
    
        # Replace all variables in the formula
        for int_var, mapped_var in var_mapping.items():
            formula = re.sub(r'\b' + re.escape(int_var) + r'\b', mapped_var, formula)
    
        return f"({formula})"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python check_candidate_implies_ground_truth_1_maxExtent.py \"formula\"\n")
        sys.stderr.write("Example: python check_candidate_implies_ground_truth_1_maxExtent.py \"(Integer_Variable_0 = 1)\"\n")
        sys.exit(1)

    translator = SMTLIBTranslator()
    formulas_file = sys.argv[1]
    formulas = list()
    with open(formulas_file) as file:
        for formula in file:
            formulas.append(formula)
    try:
        ground_truth = "(or (= Double_Variable_return 0) (or (= Double_Variable_return w) (= Double_Variable_return h)))"
        # ground_truth = "(or (not (< Double_Variable_maxx Double_Variable_minx)) (= Double_Variable_return 0))"
        # ground_truth = "(or (not (and (>= Double_Variable_maxx Double_Variable_minx) (> w h))) (= Double_Variable_return w))"
        # ground_truth = "(or (not (and (>= Double_Variable_maxx Double_Variable_minx) (<= w h))) (= Double_Variable_return h))"
        print(translator.translate_formula(formulas, ground_truth))
    except ValueError as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)
