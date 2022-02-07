import re
import json
import requests
basic_list = ['if', 'drawLine', 'drawPoint', 'drawCircle', 'drawEllipse']
basic_list_arg = [3, 7, 5, 6, 7]
valid = 0


def args(argument):
    global valid
    arg_split = argument.split(',')
    ll = []
    i = 0
    while i < len(arg_split):
        x = arg_split[i].count('(')
        y = arg_split[i].count(')')
        if x != y:
            j = i
            lol = arg_split[i]
            while x != y:
                j += 1
                lol += ',' + arg_split[j]
                x = lol.count('(')
                y = lol.count(')')
            i = j
            ll.append(lol)
        else:
            ll.append(arg_split[i])
        i += 1
    return ll


def expressions(exp):
    global valid
    seen = [0] * len(exp)
    stack = []
    dict = {}
    for i in range(len(exp)):
        if exp[i] == '(':
            stack.append(exp[i])
        elif exp[i] == ')':
            stack.pop()
        elif len(stack) != 0:
            seen[i] = 1
    if '+' in exp and seen[exp.index('+')] == 0:
        index = exp.index('+')
        dict = {
            'type': '+',
            'A': expressions(exp[:index]),
            'B': expressions(exp[index + 1:])
        }
    elif '-' in exp and seen[exp.index('-')] == 0:
        index = exp.index('-')
        dict = {
            'type': '-',
            'A': expressions(exp[:index]),
            'B': expressions(exp[index + 1:])
        }
    elif '*' in exp and seen[exp.index('*')] == 0:
        index = exp.index('*')
        dict = {
            'type': '*',
            'A': expressions(exp[:index]),
            'B': expressions(exp[index + 1:])
        }
    elif '/' in exp and seen[exp.index('/')] == 0:
        index = exp.index('/')
        dict = {
            'type': '/',
            'A': expressions(exp[:index]),
            'B': expressions(exp[index + 1:])
        }
    elif '%' in exp and seen[exp.index('%')] == 0:
        index = exp.index('%')
        dict = {
            'type': '%',
            'A': expressions(exp[:index]),
            'B': expressions(exp[index + 1:])
        }
    elif '(' in exp and ')' in exp:
        blocks = exp.index('(')
        if exp[:blocks] in basic_list:
            return function_call(exp)
        else:
            print('invalid1 \n', exp[:blocks], 'function was not defined')
            valid = 1
            return 0
    else:
        return exp

    return dict


def function_call(function):
    global valid
    s = function.find('(')
    name = function[:s]
    dict = {
        'type': "function call",
        'function name': name
    }
    stack = ['(']
    index = s + 1
    while len(stack) != 0:
        if function[index] == ')':
            stack.pop()
        elif function[index] == '(':
            stack.append('(')
        index += 1
    argument = args(function[s + 1:index - 1].replace(' ', ''))
    for i, item in enumerate(argument):
        if '(' in item:
            blocks = item.index('(')
            if item[:blocks] in basic_list:
                argument[i] = function_call(item)
            else:
                print('invalid2\n', item[:blocks], 'function was not defined')
                valid = 1
                return
    dict['args'] = argument
    it = basic_list.index(name)
    if basic_list_arg[it] != len(dict['args']):
        print('invalid\n arguments in function call are not the same number needed')
        valid = 1
        return 0

    return dict


def function_def(line):
    global valid
    s = line.find('(')
    name = line[5:s]
    if name in basic_list:
        print(basic_list)
        print('invalid3\n', name, 'already used')
        return 0
    dict = {
        'type': "function definition",
        'function name': name
    }
    stack = ['(']
    index = s + 1
    while len(stack) != 0:
        if line[index] == ')':
            stack.pop()
        elif line[index] == '(':
            stack.append('(')
        index += 1
    argument = line[s + 1:index - 1].replace(' ', '')
    argument = args(argument)
    for i, item in enumerate(argument):
        if '(' in item:
            blocks = item.index('(')
            if item[:blocks] in basic_list:
                argument[i] = function_call(item)
            else:
                print('invalid4\n', item[:blocks], 'function was not defined')
                valid = 1
                return 0
    dict['args'] = argument
    exp = line[index + 1:].replace(' ', '')
    if exp == '':
        print('invalid \neach function definition should have expression')
        valid = 1
        return 0
    dict['expression'] = expressions(exp)
    basic_list.append(name)
    basic_list_arg.append(int(len(dict['args'])))
    return dict


def r_function_def(line):
    global valid
    s = line.find('(')
    name = line[6:s]
    if name in basic_list:
        print('invalid5\n', name, 'name already used')
        valid = 1
        return 0
    dict = {
        'type': "recursive function definition",
        'function name': name
    }
    stack = ['(']
    index = s + 1
    while len(stack) != 0:
        if line[index] == ')':
            stack.pop()
        elif line[index] == '(':
            stack.append('(')
        index += 1
    argument = args(line[s + 1:index - 1].replace(' ', ''))
    for index, item in enumerate(argument):
        if '(' in item:
            blocks = item.index('(')
            if item[:blocks] in basic_list:
                argument[index] = function_call(item)
            else:
                print('invalid6\n', item[:blocks], 'function was not defined')
                valid = 1
                return 0
    r_arg = argument.pop(len(argument)-1)
    dict['args'] = argument
    dict['recursive arg'] = r_arg
    basic_list_arg.append(int(len(dict['args'])) + 1)
    return dict, name


def start(filename):
    global valid
    global basic_list
    global basic_list_arg
    basic_list_arg = [3, 7, 5, 6, 7]
    basic_list = ['if', 'drawLine', 'drawPoint', 'drawCircle', 'drawEllipse']

    with open(filename, "r") as file:
        line = file.readline()
        line = line.strip()
        line_0 = line.split(' ')
        if len(line_0) != 2 or not line_0[0].isdigit() or not line_0[1].isdigit():
            print('invalid7\nheight and width were given wrong')
            valid = 1
            return 0
        dict = {
            'height': line_0[0],
            'width': line_0[1],
            'functions': []
        }
        x = 0
        while line:
            line = file.readline()
            line_space = line.strip().split(" ")
            if line_space[0] == 'func':
                line = line.rstrip('\n')
                dict['functions'].append(function_def(line))
            elif line_space[0] == 'rfunc':
                line = line.rstrip('\n')
                dict_recursive, recursive_name = r_function_def(line)
                x = 1
            elif x == 1:
                s = re.search("\s{4}[0]{1}\s", line)
                if s is not None:
                    exp = line[6:].replace(' ', '')
                    exp = exp.strip('\n')
                    if exp == '':
                        print('invalid\neach recursive function should have base expression')
                        return 0
                    dict_recursive['base expression'] = expressions(exp)
                    x = 2
                else:
                    print("invalid8\nbase expression does not follow the given pattern")
                    return 0
            elif x == 2:
                s = re.search("\s{4}\w+\s{1}",line)
                if s is not None:
                    exp = line[s.end():].replace(' ', '')
                    exp = exp.rstrip('\n')
                    if exp == '':
                        print('invalid\neach recursive function should have recursive expression')
                        return 0
                    dict_recursive['recursive expression'] = {
                        'recursive value name': line[4:s.end()],
                        'expression': expressions(exp)
                    }
                    dict['functions'].append(dict_recursive)
                else:
                    print('invalid9\nrecursive expression does not follow the given pattern')
                    valid = 1
                    return 0
                basic_list.append(recursive_name)
                x = 0
            else:
                if not line.isspace() and line != '':
                    print('invalid10\nlines should start with func or rfunc ')
                    valid = 1
    if valid == 0:
        if 'main' not in basic_list:
            print('invalid\nprogram does not involve main function')
            return 0
        for index in range(len(dict['functions'])):
            if dict['functions'][index]['function name'] == 'main':
                if dict['functions'][index]['args'][0] == '' and len(dict['functions'][index]['args']) == 1:
                    dict['functions'][index]['args'].pop()
                else:
                    print('invalid\nmain function should not contain arguments')
                    return 0
        body = json.dumps(dict)
        r = requests.post('http://localhost:8080/job/', body)
        print(r.json())


if __name__ == '__main__':
    while True:
        print("write 1 to post a job")
        print("write 2 to check a job status")
        print("write 3 to download the result")
        choice = int(input("enter your choice: "))

        if choice == 1:
            file_name = input("please enter the file name! ")
            start(file_name)
            continue
        if choice == 2:
            job_id = input("please enter id: ")
            r = requests.get('http://localhost:8080/job/' + job_id)
            print(r.json())
            continue
        if choice == 3:
            job_id = input("please enter id: ")
            r = requests.get('http://localhost:8080/media/' + job_id)
            with open('download.jpeg', 'wb') as file:
                file.write(r.content)
            print("file downloaded :)")
            continue
