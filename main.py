import math

from Lexer import Lexer
from Parser import Parser
from interpreter import Interpreter, Context, SymbolTable, Number, BuiltInFunction

Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.pi = Number(math.pi)
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

global_symbol_table = SymbolTable()
global_symbol_table.set('Null', Number.null)
global_symbol_table.set('True', Number.false)
global_symbol_table.set('False', Number.true)
global_symbol_table.set('pi', Number.pi)
global_symbol_table.set('show', BuiltInFunction.print)
global_symbol_table.set('show_ret', BuiltInFunction.print_ret)
global_symbol_table.set('spear', BuiltInFunction.input)
global_symbol_table.set('spear_int', BuiltInFunction.input_int)
global_symbol_table.set('clear', BuiltInFunction.clear)
global_symbol_table.set('cls', BuiltInFunction.clear)
global_symbol_table.set('is_number', BuiltInFunction.is_number)
global_symbol_table.set('is_string', BuiltInFunction.is_string)
global_symbol_table.set('is_list', BuiltInFunction.is_list)
global_symbol_table.set('is_function', BuiltInFunction.is_function)
global_symbol_table.set('add', BuiltInFunction.append)
global_symbol_table.set('remove', BuiltInFunction.pop)
global_symbol_table.set('expand', BuiltInFunction.extend)
# break-> chaos_control
# return-> chaos_blast
# continue-> chaos_warp


def run(file_name, text):
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    interpreter = Interpreter()
    context = Context('<program.sdw>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error


if __name__ == '__main__':
    while True:
        text = input('Shadow > ')
        if text.strip() == '':
            continue
        if text == 'q':
            break
        result, error = run('<program.sdw>', text)

        if error:
            print(error.as_string())
        elif result:
            if len(result.elements) == 1:
                print(repr(result.elements[0]))
            else:
                print(repr(result))
