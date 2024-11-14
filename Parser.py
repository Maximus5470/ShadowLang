from Lexer import TT_INT, TT_FLOAT, TT_MUL, TT_DIV, TT_PLUS, TT_MINUS, InvalidSyntaxError, TT_EOF, TT_LPAREN, TT_RPAREN, \
    TT_POW, TT_KEYWORD, TT_IDENTIFIER, TT_EQ, TT_GTE, TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_COMMA, TT_ARROW, TT_STRING, \
    TT_LSQUARE, TT_RSQUARE, TT_NEWLINE


# Nodes

class NumberNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end

    def __repr__(self):
        return f'{self.token}'


class BinaryOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node
        self.pos_start = self.op_token.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'({self.op_token}, {self.node})'


class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token
        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end


class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node
        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.value_node.pos_end


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, step_value_node, body_node,
                 should_return_null):
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class FuncDefNode:
    def __init__(self, var_name_token, arg_name_tokens, body_node, should_return_null):
        self.var_name_token = var_name_token
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node
        self.should_return_null = should_return_null

        if self.var_name_token:
            self.pos_start = self.var_name_token.pos_start
        elif len(self.arg_name_tokens) > 0:
            self.pos_start = self.arg_name_tokens[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end


class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[-1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


class StringNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end

    def __repr__(self):
        return f'{self.token}'


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end


# Parse Result
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self


# Parser class
class Parser:
    def __init__(self, tokens):
        self.cur_token = None
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def advance(self):
        self.token_index += 1
        self.cur_token = self.tokens[self.token_index] if self.token_index < len(self.tokens) else None
        return self.cur_token

    def parse(self):
        res = self.statements()
        if not res.error and self.cur_token.type != TT_EOF:
            return res.failure(InvalidSyntaxError(self.cur_token.pos_start, self.cur_token.pos_end,
                                                  "Expected '+', '-', '*', or '/'"))
        return res

    def reverse(self, amount=1):
        self.token_index -= amount
        self.update_current_token()
        return self.cur_token

    def update_current_token(self):
        self.cur_token = self.tokens[self.token_index] if (self.token_index < len(
            self.tokens)) and self.token_index >= 0 else None

    def statements(self):
        response = ParseResult()
        statements = []
        pos_start = self.cur_token.pos_start.copy()

        while self.cur_token.type == TT_NEWLINE:
            response.register_advancement()
            self.advance()

        statement = response.register(self.expr())
        if response.error: return response
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.cur_token.type == TT_NEWLINE:
                response.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements: break
            statement = response.try_register(self.expr())
            if not statement:
                self.reverse(response.to_reverse_count)
                more_statements = False
                continue

            statements.append(statement)

        return response.success(ListNode(statements, pos_start, self.cur_token.pos_end.copy()))

    def call(self):
        response = ParseResult()
        atom = response.register(self.atom())
        if response.error: return response

        if self.cur_token.type == TT_LPAREN:
            response.register_advancement()
            self.advance()
            arg_nodes = []

            if self.cur_token.type == TT_RPAREN:
                response.register_advancement()
                self.advance()
            else:
                arg_nodes.append(response.register(self.expr()))
                if response.error:
                    return response.failure(InvalidSyntaxError(
                        self.cur_token.pos_start, self.cur_token.pos_end,
                        "Expected ')', 'var', int, float, identifier, '+', '-', '(', 'if', 'for', 'while', 'create', '['"
                    ))

                while self.cur_token.type == TT_COMMA:
                    response.register_advancement()
                    self.advance()

                    arg_nodes.append(response.register(self.expr()))
                    if response.error: return response

                if self.cur_token.type != TT_RPAREN:
                    return response.failure(InvalidSyntaxError(
                        self.cur_token.pos_start, self.cur_token.pos_end,
                        f"Expected ',' or ')'"
                    ))

                response.register_advancement()
                self.advance()

            return response.success(CallNode(atom, arg_nodes))
        return response.success(atom)

    def atom(self):
        response = ParseResult()
        token = self.cur_token

        if token.type in (TT_INT, TT_FLOAT):
            response.register_advancement()
            self.advance()
            return response.success(NumberNode(token))

        elif token.type == TT_STRING:
            response.register_advancement()
            self.advance()
            return response.success(StringNode(token))

        elif token.type == TT_IDENTIFIER:
            response.register_advancement()
            self.advance()
            return response.success(VarAccessNode(token))

        elif token.type == TT_LPAREN:
            response.register_advancement()
            self.advance()
            expr = response.register(self.expr())
            if response.error: return response
            if self.cur_token.type == TT_RPAREN:
                response.register_advancement()
                self.advance()
                return response.success(expr)
            else:
                return response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    "Expected ')'"
                ))
        elif token.type == TT_LSQUARE:
            list_expr = response.register(self.list_expr())
            if response.error: return response
            return response.success(list_expr)

        elif token.matches(TT_KEYWORD, 'if'):
            if_expr = response.register(self.if_expr())
            if response.error: return response
            return response.success(if_expr)

        elif token.matches(TT_KEYWORD, 'for'):
            for_expr = response.register(self.for_expr())
            if response.error: return response
            return response.success(for_expr)

        elif token.matches(TT_KEYWORD, 'while'):
            while_expr = response.register(self.while_expr())
            if response.error: return response
            return response.success(while_expr)

        elif token.matches(TT_KEYWORD, 'create'):
            func_def = response.register(self.func_def())
            if response.error: return response
            return response.success(func_def)

        return response.failure(InvalidSyntaxError(
            token.pos_start, token.pos_end,
            "Expected int, float, identifier, '+', '-', '(', 'if', 'for', 'while', 'create' or '['"
        ))

    def if_expr(self):
        response = ParseResult()
        all_cases = response.register(self.if_expr_cases('if'))
        if response.error: return response
        cases, else_case = all_cases
        return response.success(IfNode(cases, else_case))

    def if_expr_cases(self, case_keyword):
        response = ParseResult()
        cases = []
        else_case = None

        if not self.cur_token.matches(TT_KEYWORD, case_keyword):
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected '{case_keyword}'"
            ))

        response.register_advancement()
        self.advance()

        condition = response.register(self.expr())
        if response.error: return response

        if not self.cur_token.matches(TT_KEYWORD, 'then'):
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected 'then'"
            ))

        response.register_advancement()
        self.advance()

        if self.cur_token.type == TT_NEWLINE:
            response.register_advancement()
            self.advance()

            statements = response.register(self.statements())
            if response.error: return response
            cases.append((condition, statements, True))

            if self.cur_token.matches(TT_KEYWORD, 'end'):
                response.register_advancement()
                self.advance()
            else:
                all_cases = response.register(self.if_expr_b_or_c())
                if response.error: return response
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = response.register(self.expr())
            if response.error: return response
            cases.append((condition, expr, False))

            all_cases = response.register(self.if_expr_b_or_c())
            if response.error: return response
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return response.success((cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('elif')

    def if_expr_c(self):
        response = ParseResult()
        else_case = None

        if self.cur_token.matches(TT_KEYWORD, 'else'):
            response.register_advancement()
            self.advance()

            if self.cur_token.type == TT_NEWLINE:
                response.register_advancement()
                self.advance()

                statements = response.register(self.statements())
                if response.error: return response
                else_case = (statements, True)

                if self.cur_token.matches(TT_KEYWORD, 'end'):
                    response.register_advancement()
                    self.advance()
                else:
                    return response.failure(InvalidSyntaxError(
                        self.cur_token.pos_start, self.cur_token.pos_end,
                        "Expected 'end'"
                    ))
            else:
                expr = response.register(self.expr())
                if response.error: return response
                else_case = (expr, False)

        return response.success(else_case)

    def if_expr_b_or_c(self):
        response = ParseResult()
        cases, else_case = [], None

        if self.cur_token.matches(TT_KEYWORD, 'elif'):
            all_cases = response.register(self.if_expr_b())
            if response.error: return response
            cases, else_case = all_cases
        else:
            else_case = response.register(self.if_expr_c())
            if response.error: return response

        return response.success((cases, else_case))

    def for_expr(self):
        response = ParseResult()

        if not self.cur_token.matches(TT_KEYWORD, 'for'):
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected 'for'"
            ))

        response.register_advancement()
        self.advance()

        if self.cur_token.type != TT_IDENTIFIER:
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected identifier"
            ))

        var_name = self.cur_token
        response.register_advancement()
        self.advance()

        if self.cur_token.type != TT_EQ:
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected '='"
            ))

        response.register_advancement()
        self.advance()

        start_value = response.register(self.expr())
        if response.error: return response

        if not self.cur_token.matches(TT_KEYWORD, 'to'):
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected 'to'"
            ))

        response.register_advancement()
        self.advance()

        end_value = response.register(self.expr())
        if response.error: return response

        if self.cur_token.matches(TT_KEYWORD, 'step'):
            response.register_advancement()
            self.advance()

            step_value = response.register(self.expr())
            if response.error: return response
        else:
            step_value = None

        if not self.cur_token.matches(TT_KEYWORD, 'then'):
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected 'then'"
            ))

        response.register_advancement()
        self.advance()

        if self.cur_token.type == TT_NEWLINE:
            response.register_advancement()
            self.advance()

            body = response.register(self.statements())
            if response.error: return response

            if not self.cur_token.matches(TT_KEYWORD, 'end'):
                return response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    f"Expected 'end'"
                ))

            response.register_advancement()
            self.advance()

            return response.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = response.register(self.expr())
        if response.error: return response

        return response.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expr(self):
        response = ParseResult()

        if not self.cur_token.matches(TT_KEYWORD, 'while'):
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected 'while'"
            ))

        response.register_advancement()
        self.advance()

        condition = response.register(self.expr())
        if response.error: return response

        if not self.cur_token.matches(TT_KEYWORD, 'then'):
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected 'then'"
            ))

        response.register_advancement()
        self.advance()

        if self.cur_token.type == TT_NEWLINE:
            response.register_advancement()
            self.advance()

            body = response.register(self.statements())
            if response.error: return response

            if not self.cur_token.matches(TT_KEYWORD, 'end'):
                return (response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    f"Expected 'end'"
                )))

            response.register_advancement()
            self.advance()

            return response.success(WhileNode(condition, body, True))

        body = response.register(self.expr())
        if response.error: return response

        return response.success(WhileNode(condition, body, False))

    def func_def(self):
        response = ParseResult()

        if not self.cur_token.matches(TT_KEYWORD, 'create'):
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected 'create'"
            ))

        response.register_advancement()
        self.advance()

        if self.cur_token.type == TT_IDENTIFIER:
            var_name_tok = self.cur_token
            response.register_advancement()
            self.advance()
            if self.cur_token.type != TT_LPAREN:
                return response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    f"Expected '('"
                ))
        else:
            var_name_tok = None
            if self.cur_token.type != TT_LPAREN:
                return response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    f"Expected identifier or '('"
                ))

        response.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.cur_token.type == TT_IDENTIFIER:
            arg_name_toks.append(self.cur_token)
            response.register_advancement()
            self.advance()

            while self.cur_token.type == TT_COMMA:
                response.register_advancement()
                self.advance()

                if self.cur_token.type != TT_IDENTIFIER:
                    return response.failure(InvalidSyntaxError(
                        self.cur_token.pos_start, self.cur_token.pos_end,
                        f"Expected identifier"
                    ))

                arg_name_toks.append(self.cur_token)
                response.register_advancement()
                self.advance()

            if self.cur_token.type != TT_RPAREN:
                return response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.cur_token.type != TT_RPAREN:
                return response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    f"Expected identifier or ')'"
                ))

        response.register_advancement()
        self.advance()

        if self.cur_token.type == TT_ARROW:
            response.register_advancement()
            self.advance()

            body = response.register(self.expr())
            if response.error: return response

            return response.success(FuncDefNode(
                var_name_tok,
                arg_name_toks,
                body,
                False
            ))

        if self.cur_token.type != TT_NEWLINE:
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected '->' or NEWLINE"
            ))

        response.register_advancement()
        self.advance()

        body = response.register(self.statements())
        if response.error: return response

        if not self.cur_token.matches(TT_KEYWORD, 'end'):
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected 'end'"
            ))

        response.register_advancement()
        self.advance()

        return response.success(FuncDefNode(var_name_tok, arg_name_toks, body, True))

    def power(self):
        return self.bin_op(self.call, (TT_POW,), self.factor)

    def factor(self):
        response = ParseResult()
        token = self.cur_token

        if token.type in (TT_PLUS, TT_MINUS):
            response.register_advancement()
            self.advance()
            factor = response.register(self.factor())
            if response.error: return response
            return response.success(UnaryOpNode(token, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        response = ParseResult()

        if self.cur_token.matches(TT_KEYWORD, '!'):
            op_token = self.cur_token
            response.register_advancement()
            self.advance()

            node = response.register(self.comp_expr())
            if response.error: return response
            return response.success(UnaryOpNode(op_token, node))

        node = response.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

        if response.error:
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                "Expected int, float, identifier, '+', '-', '(' or '!', 'if', 'for', 'while', 'create' or '['"
            ))

        return response.success(node)

    def list_expr(self):
        response = ParseResult()
        element_nodes = []
        pos_start = self.cur_token.pos_start

        if self.cur_token.type != TT_LSQUARE:
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                f"Expected '['"
            ))

        response.register_advancement()
        self.advance()

        if self.cur_token.type == TT_RSQUARE:
            response.register_advancement()
            self.advance()
        else:
            element_nodes.append(response.register(self.expr()))
            if response.error:
                return response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    "Expected ']', 'var', int, float, identifier, '+', '-', '(', 'if', 'for', 'while', 'create' or '['"
                ))

            while self.cur_token.type == TT_COMMA:
                response.register_advancement()
                self.advance()

                element_nodes.append(response.register(self.expr()))
                if response.error: return response

            if self.cur_token.type != TT_RSQUARE:
                return response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    f"Expected ',' or ']'"
                ))

            response.register_advancement()
            self.advance()

        return response.success(ListNode(element_nodes, pos_start, self.cur_token.pos_end.copy()))

    def expr(self):
        response = ParseResult()

        if self.cur_token.matches(TT_KEYWORD, 'var'):
            response.register_advancement()
            self.advance()

            if self.cur_token.type != TT_IDENTIFIER:
                return response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    "Expected identifier"
                ))

            var_name = self.cur_token
            response.register_advancement()
            self.advance()

            if self.cur_token.type != TT_EQ:
                return response.failure(InvalidSyntaxError(
                    self.cur_token.pos_start, self.cur_token.pos_end,
                    "Expected '='"
                ))

            response.register_advancement()
            self.advance()
            expr = response.register(self.expr())
            if response.error: return response
            return response.success(VarAssignNode(var_name, expr))

        node = response.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, '&&'), (TT_KEYWORD, '||'))))

        if response.error:
            return response.failure(InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end,
                "Expected 'VAR', int, float, identifier, '+', '-', '(' or '!', 'if', 'for', 'while', 'create' or '['"
            ))

        return response.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.cur_token.type in ops or (self.cur_token.type, self.cur_token.value) in ops:
            op_tok = self.cur_token
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinaryOpNode(left, op_tok, right)

        return res.success(left)
