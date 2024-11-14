import os

from Lexer import TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, RunTimeError, TT_POW, TT_GTE, TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, \
    TT_KEYWORD


# Runtime Result
class RuntimeResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, response):
        if isinstance(response, RuntimeResult):
            if response.error: self.error = response.error
            return response.value
        return response

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


# Number and Value class
class Value:
    def __init__(self):
        self.context = None
        self.pos_end = None
        self.pos_start = None
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def compare_gte(self, other):
        return None, self.illegal_operation(other)

    def compare_ee(self, other):
        return None, self.illegal_operation(other)

    def compare_ne(self, other):
        return None, self.illegal_operation(other)

    def compare_lt(self, other):
        return None, self.illegal_operation(other)

    def compare_gt(self, other):
        return None, self.illegal_operation(other)

    def compare_lte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()

    def illegal_operation(self, other=None):
        if not other: other = self
        return RunTimeError(self.pos_start, other.pos_end, 'Illegal operation', self.context)


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(self.pos_start, self.pos_end, 'Division by zero', self.context)
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def compare_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def compare_ee(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def compare_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def compare_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def compare_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def compare_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start)

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        new_number = Number(self.value)
        new_number.set_pos(self.pos_start, self.pos_end)
        new_number.set_context(self.context)
        return new_number

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)


Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.pi = Number(3.14159265358979323846)


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or '<anonymous>'

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        response = RuntimeResult()
        if len(args) > len(arg_names):
            return response.failure(RunTimeError(self.pos_start, self.pos_end,
                                                 f'{len(arg_names)} arguments expected but {len(args)} given',
                                                 self.context))
        if len(args) < len(arg_names):
            return response.failure(RunTimeError(self.pos_start, self.pos_end,
                                                 f'{len(arg_names)} arguments expected but {len(args)} given',
                                                 self.context))
        return response.success(None)

    def populate_args(self, arg_names, args, context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(context)
            context.symbol_table.set(arg_name, arg_value)
        return context

    def check_and_populate_args(self, arg_names, args, context):
        response = RuntimeResult()
        response.register(self.check_args(arg_names, args))
        if response.error: return response
        response.register(self.populate_args(arg_names, args, context))
        return response.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_return_null):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_return_null = should_return_null

    def execute(self, args):
        response = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()

        exec_context.symbol_table = SymbolTable(exec_context.parent.symbol_table)
        response.register(self.check_and_populate_args(self.arg_names, args, exec_context))
        if response.error: return response

        value = response.register(interpreter.visit(self.body_node, exec_context))
        if response.error: return response

        return response.success(Number.null if self.should_return_null else value)

    def copy(self):
        new_function = Function(self.name, self.body_node, self.arg_names, self.should_return_null)
        new_function.set_context(self.context)
        new_function.set_pos(self.pos_start, self.pos_end)
        return new_function

    def __repr__(self):
        return f'<function {self.name}>'


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        new_string = String(self.value)
        new_string.set_pos(self.pos_start, self.pos_end)
        new_string.set_context(self.context)
        return new_string

    def __repr__(self):
        return self.value


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def added_to(self, other):
        new_list = List(self.elements.copy())
        new_list.elements.append(other)
        return new_list, None

    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RunTimeError(self.pos_start, self.pos_end,
                                          'Element at this index could not be removed from list because index is out of bounds',
                                          self.context)
        else:
            return None, self.illegal_operation(other)

    def multed_by(self, other):
        if isinstance(other, List):
            new_list = List(self.elements.copy())
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, self.illegal_operation(other)

    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RunTimeError(self.pos_start, self.pos_end,
                                          'Element at this index could not be retrieved from list because index is out of bounds',
                                          self.context)
        else:
            return None, self.illegal_operation(other)

    def copy(self):
        new_list = List(self.elements)
        new_list.set_pos(self.pos_start, self.pos_end)
        new_list.set_context(self.context)
        return new_list

    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        response = RuntimeResult()
        exec_context = self.generate_new_context()
        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        response.register(self.check_and_populate_args(method.arg_names, args, exec_context))
        if response.error: return response

        return_value = response.register(method(exec_context))
        if response.error: return response

        return response.success(return_value)

    def copy(self):
        new_function = BuiltInFunction(self.name)
        new_function.set_context(self.context)
        new_function.set_pos(self.pos_start, self.pos_end)
        return new_function

    def __repr__(self):
        return f'<built-in function {self.name}>'

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def execute_print(self, exec_context):
        print(str(exec_context.symbol_table.get('value')))
        return RuntimeResult().success(Number.null)

    execute_print.arg_names = ['value']

    def execute_print_ret(self, exec_context):
        print(str(exec_context.symbol_table.get('value')))
        return RuntimeResult().success(String(str(exec_context.symbol_table.get('value'))))

    execute_print_ret.arg_names = ['value']

    def execute_input(self, exec_context):
        text = input()
        return RuntimeResult().success(String(text))

    execute_input.arg_names = []

    def execute_input_int(self, exec_context):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print('Invalid input. Integer expected')
        return RuntimeResult().success(Number(number))

    execute_input_int.arg_names = []

    def execute_clear(self, exec_context):
        os.system('cls' if os.name == 'nt' else 'clear')
        return RuntimeResult().success(Number.null)

    execute_clear.arg_names = []

    def execute_is_number(self, exec_context):
        is_number = isinstance(exec_context.symbol_table.get('value'), Number)
        return RuntimeResult().success(Number.true if is_number else Number.false)

    execute_is_number.arg_names = ['value']

    def execute_is_string(self, exec_context):
        is_string = isinstance(exec_context.symbol_table.get('value'), String)
        return RuntimeResult().success(Number.true if is_string else Number.false)

    execute_is_string.arg_names = ['value']

    def execute_is_list(self, exec_context):
        is_list = isinstance(exec_context.symbol_table.get('value'), List)
        return RuntimeResult().success(Number.true if is_list else Number.false)

    execute_is_list.arg_names = ['value']

    def execute_is_function(self, exec_context):
        is_function = isinstance(exec_context.symbol_table.get('value'), BaseFunction)
        return RuntimeResult().success(Number.true if is_function else Number.false)

    execute_is_function.arg_names = ['value']

    def execute_append(self, exec_context):
        list_ = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list_, List):
            return RuntimeResult().failure(
                RunTimeError(self.pos_start, self.pos_end, 'First argument must be list', self.context))

        list_.elements.append(value)
        return RuntimeResult().success(Number.null)

    execute_append.arg_names = ['list', 'value']

    def execute_pop(self, exec_context):
        list_ = exec_context.symbol_table.get('list')
        index = exec_context.symbol_table.get('index')

        if not isinstance(list_, List):
            return RuntimeResult().failure(
                RunTimeError(self.pos_start, self.pos_end, 'First argument must be list', self.context))
        if not isinstance(index, Number):
            return RuntimeResult().failure(
                RunTimeError(self.pos_start, self.pos_end, 'Second argument must be number', self.context))

        try:
            element = list_.elements.pop(index.value)
            return RuntimeResult().success(element)
        except:
            return RuntimeResult().failure(RunTimeError(self.pos_start, self.pos_end,
                                                        'Element at this index could not be removed from list because index is out of bounds',
                                                        self.context))

    execute_pop.arg_names = ['list', 'index']

    def execute_extend(self, exec_context):
        list1 = exec_context.symbol_table.get('list1')
        list2 = exec_context.symbol_table.get('list2')

        if not isinstance(list1, List):
            return RuntimeResult().failure(
                RunTimeError(self.pos_start, self.pos_end, 'First argument must be list', self.context))
        if not isinstance(list2, List):
            return RuntimeResult().failure(
                RunTimeError(self.pos_start, self.pos_end, 'Second argument must be list', self.context))

        list1.elements.extend(list2.elements)
        return RuntimeResult().success(Number.null)

    execute_extend.arg_names = ['list1', 'list2']


BuiltInFunction.print = BuiltInFunction('print')
BuiltInFunction.print_ret = BuiltInFunction('print_ret')
BuiltInFunction.input = BuiltInFunction('input')
BuiltInFunction.input_int = BuiltInFunction('input_int')
BuiltInFunction.clear = BuiltInFunction('clear')
BuiltInFunction.is_number = BuiltInFunction('is_number')
BuiltInFunction.is_string = BuiltInFunction('is_string')
BuiltInFunction.is_list = BuiltInFunction('is_list')
BuiltInFunction.is_function = BuiltInFunction('is_function')
BuiltInFunction.append = BuiltInFunction('append')
BuiltInFunction.pop = BuiltInFunction('pop')
BuiltInFunction.extend = BuiltInFunction('extend')


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


# Interpreter class
class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_VarAccessNode(self, node, context):
        response = RuntimeResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)

        if not value:
            return response.failure(RunTimeError(node.pos_start, node.pos_end, f'{var_name} is not defined', context))

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return response.success(value)

    def visit_VarAssignNode(self, node, context):
        response = RuntimeResult()
        var_name = node.var_name_token.value
        value = response.register(self.visit(node.value_node, context))
        if response.error: return response
        context.symbol_table.set(var_name, value)
        return response.success(value)

    def visit_NumberNode(self, node, context):
        return RuntimeResult().success(
            Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinaryOpNode(self, node, context):
        response = RuntimeResult()
        left = response.register(self.visit(node.left_node, context))
        if response.error: return response
        right = response.register(self.visit(node.right_node, context))
        if response.error: return response
        result = None
        error = None

        if node.op_token.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_token.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_token.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_token.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_token.type == TT_POW:
            result, error = left.powed_by(right)
        elif node.op_token.type == TT_GTE:
            result, error = left.compare_gte(right)
        elif node.op_token.type == TT_EE:
            result, error = left.compare_ee(right)
        elif node.op_token.type == TT_NE:
            result, error = left.compare_ne(right)
        elif node.op_token.type == TT_LT:
            result, error = left.compare_lt(right)
        elif node.op_token.type == TT_GT:
            result, error = left.compare_gt(right)
        elif node.op_token.type == TT_LTE:
            result, error = left.compare_lte(right)
        elif node.op_token.matches(TT_KEYWORD, '&&'):
            result, error = left.anded_by(right)
        elif node.op_token.matches(TT_KEYWORD, '||'):
            result, error = left.ored_by(right)

        if error: return response.failure(error)
        return response.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        response = RuntimeResult()
        number = response.register(self.visit(node.node, context))
        if response.error: return response
        error = None

        if node.op_token.type == TT_MINUS:
            number, error = Number(-number.value)
        elif node.op_token.type.matches(TT_KEYWORD, '!'):
            number, error = number.notted()

        if error: return response.failure(error)
        return response.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        response = RuntimeResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = response.register(self.visit(condition, context))
            if response.error: return response
            if condition_value.is_true():
                expr_value = response.register(self.visit(expr, context))
                if response.error: return response
                return response.success(Number.null if should_return_null else expr_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            else_value = response.register(self.visit(expr, context))
            if response.error: return response
            return response.success(Number.null if should_return_null else else_value)

        return response.success(Number.null)

    def visit_ForNode(self, node, context):
        response = RuntimeResult()
        elements = []

        start_value = response.register(self.visit(node.start_value_node, context))
        if response.error: return response

        end_value = response.register(self.visit(node.end_value_node, context))
        if response.error: return response

        if node.step_value_node:
            step_value = response.register(self.visit(node.step_value_node, context))
            if response.error: return response
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value

            elements.append(response.register(self.visit(node.body_node, context)))
            if response.error: return response

        return response.success(
            Number.null if node.should_return_null else List(elements).set_context(context).set_pos(node.pos_start,
                                                                                                    node.pos_end))

    def visit_WhileNode(self, node, context):
        response = RuntimeResult()
        elements = []

        while True:
            condition = response.register(self.visit(node.condition_node, context))
            if response.error: return response

            if not condition.is_true(): break

            elements.append(response.register(self.visit(node.body_node, context)))
            if response.error: return response

        return response.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_FuncDefNode(self, node, context):
        response = RuntimeResult()
        func_name = node.var_name_token.value if node.var_name_token else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]
        func_value = Function(func_name, body_node, arg_names, node.should_return_null).set_context(context).set_pos(
            node.pos_start,
            node.pos_end)

        if node.var_name_token:
            context.symbol_table.set(func_name, func_value)

        return response.success(Number.null if node.should_return_null else func_value)

    def visit_CallNode(self, node, context):
        response = RuntimeResult()
        args = []

        value_to_call = response.register(self.visit(node.node_to_call, context))
        if response.error: return response
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(response.register(self.visit(arg_node, context)))
            if response.error: return response

        return_value = response.register(value_to_call.execute(args))
        if response.error: return response
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return response.success(return_value)

    def visit_StringNode(self, node, context):
        return RuntimeResult().success(
            String(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ListNode(self, node, context):
        response = RuntimeResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(response.register(self.visit(element_node, context)))
            if response.error: return response

        return response.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))
