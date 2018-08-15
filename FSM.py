import unittest
from abc import abstractmethod


class Context:
    def __init__(self):
        self.result = ""
        self.current_element = ""

    def get_result(self):
        return self.result


class Automater:
    def __init__(self, handlers, convert):
        self.convert = convert
        self.handlers = handlers
        self.final_results = []

    def get_res(self):
        return self.final_results

    def check_size(self):
        return len(self.handlers)

    def check_position(self):
        if self.check_size() == 0:
            return ''
        position = self.handlers[0]
        self.handlers = self.handlers[1:]
        return position

    def run_cycle(self, per, executors, current_state, context, moving):
        while per != 0:
            symbol = self.check_position()
            elem = symbol
            symbol = self.convert(symbol)
            current_state = moving[current_state][symbol]
            executors[current_state](context, elem)
            per = per - 1
        self.final_results.append(context.result)


class Splitter:
    def __init__(self):
        self.fsm: Automater = None
        self.separator = None

    def convert(self, symbol):
        if self.separator == symbol:
            return True
        else:
            return False

    def act_read_sym(self, context, symbol):
        context.current_element = symbol
        context.result = context.result + context.current_element

    def act_apply_split(self, context, symbol):
        self.fsm.final_results.append(context.result)
        context.result = ""

    def split(self, text, sep):
        self.separator = sep
        self.fsm = Automater(text, self.convert)
        context = Context()
        current_state = 'a'
        # a - state read symbols, b - state read separators
        moving = {'a': {True: 'b', False: 'a'},
                  'b': {True: 'b', False: 'a'}}

        executors = {'a': self.act_read_sym, 'b': self.act_apply_split}
        per = len(text)
        per += 1
        self.fsm.run_cycle(per, executors, current_state, context, moving)
        return self.fsm.get_res()

########################################################################################################################


class Token:
    @abstractmethod
    def value(self):
        pass


class FloatToken:
    def __init__(self, value):
        self._value = value

    def value(self):
        return self._value

    def __str__(self) -> str:
        return "FloatToken({})".format(self._value)

    def __repr__(self) -> str:
        return self.__str__()


class OperationToken:
    def __init__(self, value):
        self._value = value

    def value(self):
        return self._value

    def __str__(self) -> str:
        return "OperationToken({})".format(self._value)

    def __repr__(self) -> str:
        return self.__str__()


class NumberToken:
    def __init__(self, value):
        self._value = value

    def value(self):
        return self._value

    def __str__(self) -> str:
        return "NumberToken({})".format(self._value)

    def __repr__(self) -> str:
        return self.__str__()


class Tokenizer:
    def __init__(self):
        self.fsm: Automater = None
        self.signs = ["+", "-", "*", ":"]

    def convert(self, symbol):

        for sign in self.signs:
            if sign == symbol:
                return "Sign"
        if symbol == ",":
            return "Float"
        elif symbol == " ":
            return "Sep"
        else:
            return "Num"

    def act_read_sym(self, context, symbol):
        context.current_element = symbol
        context.result = context.result + context.current_element
        # self.fsm.final_results.append(NumberToken(context.result))

    def act_read_sign(self, context, symbol):
        context.current_element = symbol
        context.result = context.result + context.current_element
        self.fsm.final_results.append(OperationToken(context.result))
        context.result = None

    def act_num_after_num(self, context, symbol):
        context.current_element = symbol
        context.result = context.result + context.current_element
        self.fsm.final_results.append(NumberToken(context.result))
        context.result = None

    def act_num_after_float(self, context, symbol):
        context.current_element = symbol
        context.result = context.result + context.current_element
        self.fsm.final_results.append(FloatToken(context.result))
        context.result = None

    def act_read_float(self, context, symbol):
        context.current_element = symbol
        context.result = context.result + context.current_element

    def act_read_sep_af(self, context, symbol):
        self.fsm.final_results.append(NumberToken(context.result))
        context.result = ""
        # self.fsm.final_results.append(" ")

    def act_read_sep(self, context, symbol):
        context.result = ""
        # self.fsm.final_results.append(" ")

    @abstractmethod
    def tokenize(self, expression: str) -> list:
        self.fsm = Automater(expression, self.convert)
        context = Context()
        current_state = 'Start'
        # num - state read first number, sign - state read sign (+ - * :), sep - state read " ", float - state read ","
        # num_after_num - state read number after other number, num_after_float - state read number after float
        # TODO # change float # add num_after_num # num_after_float #

        moving = {"Start": {"Num": "Num"},
                  "Num": {"Num": "num_after_num", "Sign": 'Sign', "Float": "Float", "Sep": "Sep_af",
                          "num_after_float": "num_after_float", "num_after_num": "num_after_num"},
                  "Sign": {"Num": "Num", "Sign": "Sign", "Sep": "Sep"},
                  "Float": {"Num": "num_after_float", "Float": "Float", "Sep": "Sep"},
                  "Sep": {"Num": "Num", "Sep": "Sep", "Sign": 'Sign', "Float": "Float"},
                  "Sep_af": {"Num": "Num", "Sep": "Sep", "Sign": 'Sign', "Float": "Float"},
                  "num_after_num": {"num_after_num": "num_after_num", "Sep": "Sep"},
                  "num_after_float": {"num_after_float": "num_after_float", "Sep": "Sep"}}

        executors = {"Num": self.act_read_sym, "Sign": self.act_read_sign, "Float": self.act_read_float,
                     "Sep": self.act_read_sep, "num_after_num": self.act_num_after_num,
                     "num_after_float": self.act_num_after_float, "Sep_af": self.act_read_sep_af}

        per = len(expression)
        self.fsm.run_cycle(per, executors, current_state, context, moving)
        return self.fsm.get_res()


class TestSplitter(unittest.TestCase):
    def test_one(self):
        spl = Splitter()
        res = spl.split("e3d", '3')
        self.assertListEqual(["e", "d"], res)

    def test_two(self):
        spl = Splitter()
        res = spl.split("hello world how are you", ' ')
        self.assertListEqual(["hello", "world", "how", "are", "you"], res)

    def test_three(self):
        spl = Splitter()
        res = spl.split("abc", ' ')
        self.assertListEqual(["abc"], res)


if __name__ == '__main__':
    unittest.main()
