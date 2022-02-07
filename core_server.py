from PIL import Image, ImageDraw

from client import expressions
from shared import data as sdata


def job_create(dict, output_name):
    instance = Draw()
    instance.run(dict, output_name)


class Draw:

    original_dict = None
    pillow_functions = ['drawLine', 'drawPoint', 'drawCircle', 'drawEllipse']
    height = None
    width = None
    img = None
    draw = None
    valid = 0

    def draw_function(self, given_arguments, list_arguments, dict_expression):
        x0 = self.expressions(given_arguments, list_arguments, dict_expression['args'][0])
        y0 = self.expressions(given_arguments, list_arguments, dict_expression['args'][1])
        r = self.expressions(given_arguments, list_arguments, dict_expression['args'][-3])
        g = self.expressions(given_arguments, list_arguments, dict_expression['args'][-2])
        b = self.expressions(given_arguments, list_arguments, dict_expression['args'][-1])
        if 255 < r or r < 0 or 255 < g or g < 0 or 255 < b or b < 0:
            self.valid = 1
        else:
            if dict_expression['function name'] == 'drawLine':
                x1 = self.expressions(given_arguments, list_arguments, dict_expression['args'][2])
                y1 = self.expressions(given_arguments, list_arguments, dict_expression['args'][3])
                self.draw.line((x0, y0, x1, y1), fill=(r, g, b))
            elif dict_expression['name'] == 'drawPoint':
                self.draw.point((x0, y0), fill=(r, g, b))
            elif dict_expression['name'] == 'drawCircle':
                radius = given_arguments[list_arguments.index(dict_expression['args'][2])]
                self.draw.ellipse((x0, y0, radius, radius), fill=(r, g, b))
            elif dict_expression['name'] == 'drawEllipse':
                x1 = self.expressions(given_arguments, list_arguments, dict_expression['args'][2])
                y1 = self.expressions(given_arguments, list_arguments, dict_expression['args'][3])
                self.draw.ellipse((x0, y0, x1, y1), fill=(r, g, b))
        return 0

    def expressions(self, given_arguments, list_arguments, dict_expression):
        if not isinstance(dict_expression, dict):
            if dict_expression.isdigit():
                if int(dict_expression) < 0:
                    self.valid = 2
                return int(dict_expression)
            else:
                s = list_arguments.index(dict_expression)
                if int(given_arguments[s]) < 0:
                    self.valid = 2
                return int(given_arguments[s])
        elif dict_expression['type'] == 'function call':
            if dict_expression['function name'] in self.pillow_functions:
                return self.draw_function(given_arguments, list_arguments, dict_expression)
            else:
                return self.check_which_function(given_arguments, list_arguments, dict_expression)
        elif dict_expression['type'] == '+':
            x = self.expressions(given_arguments, list_arguments, dict_expression['A'])
            y = self.expressions(given_arguments, list_arguments, dict_expression['B'])
            return int(x + y)
        elif dict_expression['type'] == '-':
            x = self.expressions(given_arguments, list_arguments, dict_expression['A'])
            y = self.expressions(given_arguments, list_arguments, dict_expression['B'])
            return int(x - y)
        elif dict_expression['type'] == '*':
            x = self.expressions(given_arguments, list_arguments, dict_expression['A'])
            y = self.expressions(given_arguments, list_arguments, dict_expression['B'])
            return int(x * y)
        elif dict_expression['type'] == '/':
            x = self.expressions(given_arguments, list_arguments, dict_expression['A'])
            y = self.expressions(given_arguments, list_arguments, dict_expression['B'])
            return int(x / y)
        elif dict_expression['type'] == '%':
            x = self.expressions(given_arguments, list_arguments, dict_expression['A'])
            y = self.expressions(given_arguments, list_arguments, dict_expression['B'])
            return int(x % y)

    def read_if(self, given_arguments, list_arguments, function):
        cond = expressions(given_arguments, list_arguments, function['args'][0])
        if cond == 0:
            return expressions(given_arguments, list_arguments, function['args'][2])
        else:
            return expressions(given_arguments, list_arguments, function['args'][1])

    def read_function(self, given_arguments, list_arguments, function):
        list_functions = self.original_dict['functions']
        for index in range(len(list_functions)):
            if list_functions[index]['function name'] == function['function name']:
                if function['function name'] == 'if':
                    return self.read_if(given_arguments, list_arguments, list_functions[index]['expression'])
                else:
                    return self.expressions(given_arguments, list_arguments, list_functions[index]['expression'])

    def read_recursive_function(self, given_arguments, list_arguments, function):
        list_functions = self.original_dict['functions']
        for index in range(len(list_functions)):
            if list_functions[index]['function name'] == function['function name']:
                given_arguments.append(0)
                list_arguments.append(list_functions[index]['recursive expression']['recursive value name'])
                rec_arg = list_arguments.index(list_functions[index]['recursive arg'])
                for i in range(int(given_arguments[rec_arg])):
                    given_arguments[rec_arg] = i
                    if i == 0:
                        self.expressions(given_arguments, list_arguments, list_functions[index]['base expression'])
                    else:
                        given_arguments[-1] = self.expressions(given_arguments, list_arguments,
                                                          list_functions[index]['recursive expression']['expression'])

    def check_which_function(self, list, list2, dict_test):
        list_functions = self.original_dict['functions']
        for index in range(len(list_functions)):
            if list_functions[index]['function name'] == dict_test['function name']:
                if list_functions[index]['type'] == 'function definition':
                    return self.read_function(list, list2, dict_test)
                elif list_functions[index]['type'] == 'recursive function definition':
                    return self.read_recursive_function(list, list2, dict_test)

    def init(self, dict):
        self.original_dict = dict
        self.height = int(self.original_dict['height'])
        self.width = int(self.original_dict['width'])
        self.img = Image.new("RGB", (self.height, self.width))
        self.draw = ImageDraw.Draw(self.img)

    def run(self, dict, id):
        sdata.status_map[id] = 'running'
        self.init(dict)

        list_functions = self.original_dict['functions']
        for index in range(len(list_functions)):
            if list_functions[index]['function name'] == 'main':
                ll = list_functions[index]['expression']['args']
                for item in range(len(list_functions)):
                    if list_functions[item]['function name'] == list_functions[index]['expression']['function name']:
                        lol = list_functions[item]['args']
                        if list_functions[item]['type'] == 'recursive function definition':
                            lol.append(list_functions[item]['recursive arg'])
                        self.check_which_function(ll, lol, list_functions[index]['expression'])
        self.img.save(id + '.jpeg', "JPEG")
        sdata.status_map[id] = 'done'
        if self.valid == 0:
            print(sdata.status_map)
        elif self.valid == 1:
            print('invalid\nr g b were given wrong')
        elif self.valid == 2:
            print('invalid\nthere is a negative number given in program')
