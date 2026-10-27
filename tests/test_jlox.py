"""End-to-end tests using only Python's standard library and a JDK."""

from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]


class JloxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / "build").mkdir(exist_ok=True)
        cls.workspace = tempfile.TemporaryDirectory(prefix="jlox-tests-", dir=ROOT / "build")
        cls.addClassCleanup(cls.workspace.cleanup)
        cls.work = Path(cls.workspace.name)
        cls.classes = cls.work / "classes"
        cls.classes.mkdir()
        cls.sources = sorted((ROOT / "jlox").glob("*.java"))
        cls.compile(cls.classes, cls.sources + [ROOT / "tool" / "GenerateAst.java"])

    @staticmethod
    def compile(destination, sources):
        result = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-cp", str(destination),
             "-d", str(destination), *map(str, sources)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    def run_lox(self, source, *, classes=None, prompt=False):
        command = ["java", "-cp", str(classes or self.classes), "jlox.Lox"]
        if not prompt:
            script = self.work / "test program.lox"
            script.write_text(textwrap.dedent(source), encoding="utf-8")
            command.append(str(script))
        return subprocess.run(
            command, input=source if prompt else None,
            capture_output=True, text=True, encoding="utf-8", timeout=10,
        )

    def assert_output(self, source, expected, **kwargs):
        result = self.run_lox(source, **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, textwrap.dedent(expected).lstrip("\n"))

    def test_arithmetic_precedence_and_comparisons(self):
        self.assert_output("""
            print 1 + 2 * 3;
            print (1 + 2) * 3;
            print -12 / 3 - 1;
            print 1.5 + 2.25;
            print 3 > 2;
            print 3 >= 3;
            print 2 < 3;
            print 2 <= 2;
        """, "7\n9\n-5\n3.75\ntrue\ntrue\ntrue\ntrue\n")

    def test_false_negation_and_truthiness(self):
        self.assert_output("""
            print false;
            print !false;
            print !true;
            print !nil;
            print !!0;
            print !"";
        """, "false\ntrue\nfalse\ntrue\ntrue\nfalse\n")

    def test_identifiers_starting_with_o_and_keyword_prefixes(self):
        self.assert_output("""
            var o = 1;
            var orange = 2;
            var order = 3;
            var orbit = 4;
            var falsehood = 5;
            print o + orange + order + orbit + falsehood;
        """, "15\n")

    def test_equality_for_all_value_types(self):
        self.assert_output("""
            print "lox" == "lox";
            print "lox" != "java";
            print true == true;
            print false != true;
            print nil == nil;
            print nil != 0;
            print 1 == "1";
            print 1 != 2;
            class Thing {}
            var a = Thing();
            print a == a;
            print a == Thing();
            fun f() {}
            print f == f;
        """, "true\ntrue\ntrue\ntrue\ntrue\ntrue\nfalse\ntrue\ntrue\nfalse\ntrue\n")

    def test_logical_values_and_short_circuit_side_effects(self):
        self.assert_output("""
            var touched = 0;
            print false and (touched = 1);
            print true or (touched = 2);
            print touched;
            print false or "fallback";
            print true and "right";
            print nil or 42;
            print nil and missing;
            print "left" or missing;
            print false or true and false;
        """, "false\ntrue\n0\nfallback\nright\n42\nnil\nleft\nfalse\n")

    def test_variables_blocks_and_assignment(self):
        self.assert_output("""
            var a;
            print a;
            a = "global";
            { var a = "local"; print a; a = "updated"; print a; }
            print a;
            var b = 0;
            var c = 0;
            b = c = 7;
            print b + c;
        """, "nil\nlocal\nupdated\nglobal\n14\n")

    def test_if_while_and_for_variants(self):
        self.assert_output("""
            if (false) print "wrong"; else print "else";
            if (true) print "then";
            var n = 0;
            while (n < 2) { print n; n = n + 1; }
            for (var i = 0; i < 2; i = i + 1) print i;
            for (n = 2; n < 4;) { print n; n = n + 1; }
            fun forever() { for (;;) return "done"; }
            print forever();
        """, "else\nthen\n0\n1\n0\n1\n2\n3\ndone\n")

    def test_functions_recursion_and_return(self):
        self.assert_output("""
            fun fib(n) {
              if (n <= 1) return n;
              return fib(n - 1) + fib(n - 2);
            }
            print fib(8);
            fun empty() {}
            fun early() { return; print "unreachable"; }
            print empty();
            print early();
            print fib;
            print clock() > 0;
        """, "21\nnil\nnil\n<fn fib>\ntrue\n")

    def test_closures_and_lexical_resolution(self):
        self.assert_output("""
            fun makeCounter() {
              var i = 0;
              fun count() { i = i + 1; return i; }
              return count;
            }
            var first = makeCounter();
            var second = makeCounter();
            print first(); print first(); print second();
            var a = "global";
            {
              fun showA() { print a; }
              showA();
              var a = "block";
              showA();
            }
        """, "1\n2\n1\nglobal\nglobal\n")

    def test_classes_inheritance_this_super_and_bound_methods(self):
        self.assert_output("""
            class Base {
              init(value) { this.value = value; return; }
              say() { return this.value; }
            }
            class Child < Base {
              say() { return super.say() + "!"; }
              closure() {
                fun nested() { return super.say() + this.value; }
                return nested;
              }
            }
            var child = Child("hello");
            print child.say();
            var method = child.say;
            child.value = "bye";
            print method();
            print child.closure()();
            print child.init("reset") == child;
            child.say = "field";
            print child.say;
            print Child;
            print child;
        """, "hello!\nbye!\nbyebye\ntrue\nfield\nChild\nChild instance\n")

    def test_comments_and_multiline_strings(self):
        self.assert_output('''
            // A comment before code.
            print "first
            second"; // Another comment.
            print "// inside a string";
        ''', "first\nsecond\n// inside a string\n")

    def test_compile_errors_exit_65_without_executing(self):
        cases = [
            ('print "must not run"; var a = ;', "Expect expression"),
            ('print "unterminated', "Unterminated String"),
            ('@', "Unexpected Character"),
            ('print (1 + 2;', "Expect ')'"),
            ('{ var a = 1;', "Expect '}'"),
            ('var a = 1', "Expect ';'"),
            ('return 1;', "Can't return"),
            ('print this;', "Can't use 'this'"),
            ('super.method();', "Can't use 'super'"),
            ('class A { method() { super.method(); } }', "no superclass"),
            ('class A < A {}', "Inherit from itself"),
            ('class A { init() { return 1; } }', "return a value"),
            ('{ var a = a; }', "Own Initializer"),
            ('{ var a; var a; }', "Already a variable"),
            ('fun f(a, a) {}', "Already a variable"),
            ('1 = 2;', "Invalid assignment target"),
        ]
        for source, message in cases:
            with self.subTest(source=source):
                result = self.run_lox(source)
                self.assertEqual(result.returncode, 65, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn(message, result.stderr)
                self.assertIn("[line ", result.stderr)
                self.assertNotIn("Exception", result.stderr)

    def test_runtime_errors_exit_70(self):
        cases = [
            ('print missing;', "Undefined Variable"),
            ('missing = 1;', "Undefined variable"),
            ('print 1 + "x";', "Operands must be"),
            ('print "x" - 1;', "Operands Must Be Numbers"),
            ('print -"x";', "Operand Must Be"),
            ('123();', "Can Only Call"),
            ('fun f(a) {} f();', "Expected 1 arguments but got 0"),
            ('print 1.foo;', "Only instances"),
            ('var n = 1; n.foo = 2;', "Only Instances"),
            ('class A {} print A().missing;', "Property"),
            ('var A = 1; class B < A {}', "Superclass must be a class"),
            ('class A {} class B < A { m() { super.missing(); } } B().m();', "Property"),
        ]
        for source, message in cases:
            with self.subTest(source=source):
                result = self.run_lox(source)
                self.assertEqual(result.returncode, 70, result.stderr)
                self.assertIn(message, result.stderr)
                self.assertIn("[line ", result.stderr)
                self.assertNotIn("Exception", result.stderr)

    def test_prompt_persists_state_and_recovers_after_errors(self):
        result = self.run_lox(
            'var orange = 10;\nprint orange;\nprint ;\nprint missing;\n'
            '{ var local = 1; print missing; }\nprint orange + 1;\n'
            'fun f() { return orange; }\nprint f();\n', prompt=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '> > 10\n> > > > 11\n> > 10\n> ')
        self.assertIn("Expect expression", result.stderr)
        self.assertIn("Undefined Variable", result.stderr)
        self.assertNotIn("Exception", result.stderr)

    def test_command_line_usage_and_missing_file(self):
        command = ["java", "-cp", str(self.classes), "jlox.Lox"]
        usage = subprocess.run(command + ["a", "b"], capture_output=True, text=True, timeout=10)
        self.assertEqual(usage.returncode, 64)
        self.assertIn("Usage: jlox [script]", usage.stdout)
        missing = subprocess.run(
            command + [str(self.work / "missing.lox")], capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(missing.returncode, 74)
        self.assertIn("Could not read file", missing.stderr)
        self.assertNotIn("Exception", missing.stderr)

    def test_prompt_multiline_closure(self):
        result = self.run_lox(textwrap.dedent('''\
            print "Closures retain their state:";
            fun makeCounter() {
              var count = 0;
              fun next() {
                count = count + 1;
                return count;
              }
              return next;
            }
            var counter = makeCounter();
            print counter();
            print counter();
        '''), prompt=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            result.stdout,
            '> Closures retain their state:\n> ' + '... ' * 7 + '> > 1\n> 2\n> ',
        )

    def test_prompt_multiline_class_and_inheritance(self):
        result = self.run_lox(textwrap.dedent('''\
            class Greeter{
              init(name) {
                this.name = name;
              }
              greet() {
                return "Hello, " + this.name;
              }
            }
            class Child < Greeter {
              greet() { return super.greet() + "!"; }
            }
            print Child("Lox").greet();
        '''), prompt=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertTrue(result.stdout.endswith('> Hello, Lox!\n> '), result.stdout)
        self.assertIn('... ', result.stdout)

    def test_prompt_multiline_expressions_and_statements(self):
        result = self.run_lox(textwrap.dedent('''\
            var total =
              1 +
              2;
            print (
              total * 2
            );
            if (true)
              print "then";
            for (var i = 0;
                 i < 2;
                 i = i + 1) {
              print i;
            }
            print total
            ;
        '''), prompt=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            result.stdout.replace('... ', '').replace('> ', ''),
            '6\nthen\n0\n1\n3\n',
        )

    def test_prompt_multiline_strings_and_comments(self):
        result = self.run_lox(
            '{\n// Ignore delimiters: } ) "\n'
            'print "} ( // text";\n\n}\n'
            'print "first\nsecond";\n', prompt=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            result.stdout.replace('... ', '').replace('> ', ''),
            '} ( // text\nfirst\nsecond\n',
        )

    def test_prompt_waits_before_executing_any_partial_submission(self):
        result = self.run_lox(
            'var count = 0;\ncount = count + 1; fun f() {\n'
            'return count;\n}\nprint f();\n', prompt=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, '> > ... ... > 1\n> ')

    def test_prompt_incomplete_input_at_eof_reports_error(self):
        for source, message in [
            ('class Greeter{\n', "Expect '}' after class body"),
            ('fun f() {\nreturn 1;\n', "Expect '}' after block"),
            ('print "first\n', "Unterminated String"),
            ('print 1\n', "Expect ';'"),
        ]:
            with self.subTest(source=source):
                result = self.run_lox(source, prompt=True)
                self.assertEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertIn('... ', result.stdout)
                self.assertNotIn('Exception', result.stderr)

    def test_prompt_cancel_and_error_recovery(self):
        result = self.run_lox(
            'var count = 0;\ncount = count + 1; fun abandoned() {\n'
            ':cancel\nprint count;\n'
            'print ; fun invalid() {\nprint 42;\n'
            'fun valid() {\nreturn 7;\n}\nprint valid();\n',
            prompt=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.replace('... ', '').replace('> ', ''),
            '0\n42\n7\n',
        )
        self.assertIn('Expect expression', result.stderr)
        self.assertNotIn('Exception', result.stderr)

    def test_prompt_pasted_demo(self):
        result = self.run_lox(
            (ROOT / "examples" / "demo.lox").read_text(encoding="utf-8"),
            prompt=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            result.stdout.replace('... ', '').replace('> ', ''),
            (ROOT / "examples" / "demo.expected").read_text(encoding="utf-8"),
        )

    def test_empty_program(self):
        self.assert_output("", "")

    def test_demo(self):
        self.assert_output(
            (ROOT / "examples" / "demo.lox").read_text(encoding="utf-8"),
            (ROOT / "examples" / "demo.expected").read_text(encoding="utf-8"),
        )

    def test_generated_ast_compiles_and_runs_demo(self):
        generated = self.work / "generated" / "jlox"
        result = subprocess.run(
            ["java", "-cp", str(self.classes), "tool.GenerateAst", str(generated)],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        fresh_classes = self.work / "regenerated-classes"
        fresh_classes.mkdir()
        sources = [p for p in self.sources if p.name not in ("Expr.java", "Stmt.java")]
        self.compile(fresh_classes, sources + sorted(generated.glob("*.java")))
        self.assert_output(
            (ROOT / "examples" / "demo.lox").read_text(encoding="utf-8"),
            (ROOT / "examples" / "demo.expected").read_text(encoding="utf-8"),
            classes=fresh_classes,
        )


if __name__ == "__main__":
    unittest.main()
