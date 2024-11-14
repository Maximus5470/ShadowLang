# ShadowLang


Welcome to **ShadowLang**, a minimalist programming language developed entirely in Python. ShadowLang was created with simplicity and flexibility in mind, providing essential functionality for arithmetic, logical operations, and control flow, making it a powerful and intuitive tool for scripting and computation tasks.

**Technologies used:**
- **Python**
- **Lexical Analysis**
- **Parsing**
- **Interpreter Design**

## Table of Contents

- [Features](#features)
- [Grammar Overview](#grammar-overview)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Acknowledgements](#acknowledgements)

---

## Features

ShadowLang offers a streamlined syntax and set of features that make it ideal for lightweight programming tasks:

- **Variable Declaration**: Define variables and assign values with ease.
- **Basic Arithmetic and Comparison Operators**: Support for operations like addition, subtraction, multiplication, division, and comparison (e.g., `==`, `<`, `>`, `<=`, `>=`).
- **Logical Expressions**: Includes `AND`, `OR`, and `NOT` operators.
- **Control Flow**: Conditional statements (`IF`, `ELIF`, `ELSE`) and loop constructs (`FOR`, `WHILE`).
- **Function Definitions**: Define reusable code blocks with the `CREATE` keyword.
- **List Handling**: Inline list expressions for storing and manipulating collections of values.
- **Power and Exponentiation**: Support for power calculations with the `POW` keyword.
- **Python-Based Interpreter**: Built entirely in Python, making it highly portable and easy to extend.

## Grammar Overview

ShadowLang has a simple yet expressive grammar, inspired by Python and other scripting languages. The core grammar is as follows:

- **Statements**: Consist of expressions separated by newlines.
- **Expressions**: Support variable declarations, arithmetic and comparison operations, and logical combinations.
- **Functions**: Defined with the `create` keyword, functions support multiple arguments and return values.
- **Control Flow**: Includes `if`, `elif`, `else`, `for`, and `while` constructs for versatile programming logic.

### Grammar Rules

```plaintext
statements: NEWLINE* expr (NEWLINE+ expr)* NEWLINE*

expr:   KEYWORD: var IDENTIFIER EQ expr
        term((PLUS|MINUS) term)*
        comparison-expr((KEYWORD: AND|OR) comparison-expr)*

comparison-expr:    NOT comparison-expr
                    arithmetic-expr ((EE|LT|GT|LTE|GTE) arithmetic-expr)*

arithmetic-expr: term((PLUS|MINUS) term)*

term:   factor((MUL|DIV) factor)*

factor: (PLUS|MINUS) factor
        power

power:  call(POW factor)*

call:   atom(LPAREN (expr (COMMA expr)*)? RPAREN)?

atom:   INT|FLOAT|STRING|IDENTIFIER
        LPAREN expr RPAREN
        list-expr
        if-expr
        for-expr
        while-expr
        func-def

list-expr:  LSQUARE (expr (COMMA expr)*)? RSQUARE

if-expr:    KEYWORD: IF expr KEYWORD: THEN
            (expr if-expr-b|if-expr-c?)
            (NEWLINE statements KEYWORD: END if-expr-b|if-expr-c)

if-expr-b:  KEYWORD: ELIF expr KEYWORD: THEN
            (expr if-expr-b|if-expr-c?)
            (NEWLINE statements KEYWORD: END if-expr-b|if-expr-c)

if-expr-c:  KEYWORD: ELSE
            expr
            (NEWLINE statements KEYWORD: END)

for-expr:   KEYWORD: FOR IDENTIFIER EQ expr KEYWORD: TO expr
            (KEYWORD: STEP expr)? KEYWORD: THEN
            expr
            (NEWLINE statements KEYWORD: END)

while-expr: KEYWORD: WHILE expr KEYWORD: THEN
            expr
            (NEWLINE statements KEYWORD: END)

func-def:   KEYWORD: CREATE IDENTIFIER?
            LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN
            (ARROW: expr)
            (NEWLINE statements KEYWORD: END)
```
## Installation

Since ShadowLang is built with Python, you only need Python installed on your machine.

1. Clone the repository:

   ```bash
   git clone https://github.com/Maximus5470/ShadowLang.git
   cd ShadowLang
2. Run the main interpreter:
   ```bash
   python main.py

## Getting Started

Once installed, you can start writing scripts in ShadowLang or try out examples directly in the interactive interpreter.

### Example: Variable Assignment and Arithmetic

```plaintext
var x = 5
var y = 10
var result = x + y
```
###Example: Control Flow and Functions

```plaintext
create greet(name)
  show("Hello, " + name)
end

greet("ShadowLang")
```

## Acknowledgements
ShadowLang is inspired by various minimalist languages and scripting environments. Built as a personal project to deepen my understanding of interpreters and language design.
