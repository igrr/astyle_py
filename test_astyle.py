import unittest
import astyle_py.astyle_wrapper as astyle


class AstyleTest(unittest.TestCase):
    def test_version(self):
        obj = astyle.Astyle()
        self.assertEqual("3.1", obj.version())

    def test_args(self):
        args = astyle.parse_args(["--quiet", "--dry-run", "--exclude=foo.c", "bar.c", "baz.c"])
        self.assertEqual(True, args.quiet)
        self.assertEqual(False, args.fix_formatting)
        self.assertListEqual(["bar.c", "baz.c"], args.files)
        self.assertListEqual(["foo.c"], args.exclude_list)

        self.assertRaisesRegex(ValueError, "Option exclude requires a value", astyle.parse_args, ["--exclude"])


if __name__ == '__main__':
    unittest.main()
