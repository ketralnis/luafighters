import unittest

from luafighters.executor import BoardExecutor


class TestLuaLibraries(unittest.TestCase):
    def setUp(self):
        self.ex = BoardExecutor('return')

    def test_pathfinding(self):
        def _tester(program):
            vals = self.ex.lua.sandboxed_load(program)()
            vals = [l.to_python() for l in vals]
            return tuple(vals)

        res = _tester("""
            return find_path(5, 5, 0, 0)
        """)
        self.assertEqual(res, (4.0, 4.0))

        res = _tester("""
            return find_path(0, 0, 0, 0)
        """)
        self.assertEqual(res, (0.0, 0.0))

        res = _tester("""
            return find_path(5, 0, 2, 0)
        """)
        self.assertEqual(res, (4.0, 0.0))

if __name__ == '__main__':
    unittest.main()
