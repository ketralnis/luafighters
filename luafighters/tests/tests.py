import unittest
import time

from luafighters.executor import execute

class TestLuaExecution(unittest.TestCase):
    def test_basics1(self):
        program = """
            return 1
        """
        self.assertEqual(execute(program),
                         (1.0,))

    def test_basics2(self):
        program = """
            return a, b, a+b
        """
        self.assertEqual(execute(program, a=1, b=2),
                         (1.0, 2.0, 3.0))

    def test_basics3(self):
        program = """
            foo = {}
            while #foo < 5 do
                foo[#foo+1] = #foo+1
            end
            return foo
        """
        self.assertEqual(execute(program),
                         ({1.0: 1.0,
                           2.0: 2.0,
                           3.0: 3.0,
                           4.0: 4.0,
                           5.0: 5.0},))

    def test_serialize_deserialize(self):
        program = """
            return foo
        """
        input = {
            1: 2,
            2: 3,
            4: "abc",
            # 5: ['a', 'b', 'c'], # TODO
            6: 6.5,
            7: None,
            8: '',
            9: True,
            10: False,
            11: {'a': {1: 2}}
        }
        expected_output = {
            1.0: 2.0,
            2.0: 3.0,
            4.0: "abc",
            # 5.0: {1.0: 'a', 2.0: 'b', 3.0: 'c'},
            6.0: 6.5,
            # 7 disappears
            8.0: '',
            9.0: True,
            10.0: False,
            11.0: {'a': {1.0: 2.0}}
            }

        self.assertEqual(execute(program,
                                 foo=input),
                         (expected_output,))

    def test_no_weird_python_types(self):
        program = """
            return foo
        """
        with self.assertRaises(TypeError):
            execute(program, foo=object())

        with self.assertRaises(TypeError):
            execute(program, foo=set())
        # TODO we need test_no_weird_lua_types too

    def test_assertions(self):
        program = """
            assert false
        """
        with self.assertRaises(RuntimeError):
            execute(program)

        program = """
            error("nuh uh")
        """
        with self.assertRaises(RuntimeError):
            execute(program)


class TestSafeguards(unittest.TestCase):
    def test_memory(self):
        program = """
            foo = {}
            while #foo < 50000000 do
                foo[#foo+1] = 1
            end
            return 1
        """
        with self.assertRaises(RuntimeError):
            execute(program)

    def test_timeout(self):
        program = """
            foo = {}
            while true do
            end
            return 1
        """
        with self.assertRaises(RuntimeError):
            execute(program)

    def test_no_print(self):
        # make sure we didn't pass any libraries to the client program
        program = """
            print(foo)
            return 0
        """
        with self.assertRaises(RuntimeError):
            execute(program, foo=0)

    def test_no_regex(self):
        # there are some regex operations you can do that are super slow, so we
        # block regexes entirely
        program = """
            return string.find(("a"):rep(1e4), ".-.-.-.-b$")
        """

        started = time.time()
        with self.assertRaises(RuntimeError):
            execute(program)

        self.assertLess(time.time() - started, 1.0)

    def test_have_good_libs(self):
        # make sure we did pass the libraries that are okay
        program = """
            math.abs(-1)
            table.sort({})
            return foo
        """
        execute(program, foo=0)


if __name__ == '__main__':
    unittest.main()
