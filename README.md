
# Lox interpreter

A Java implementation of Lox from Bob Nystrom's *Crafting Interpreters*, with
variables, lexical scope, control flow, functions, closures, classes, and inheritance.

## Run the demo (Windows / PowerShell)

Install a JDK (Java 8 or newer) and make sure `java` and `javac` are on your PATH.
From the repository root:

```powershell
.\run.ps1 examples/demo.lox
```

The launcher compiles the Java sources into `build/classes` before running them.
The demo shows arithmetic, booleans, recursive Fibonacci, a stateful closure, and
classes with inheritance and bound methods. Expected output is in
[`examples/demo.expected`](examples/demo.expected); it ends with `=== Demo complete ===`.

If PowerShell blocks local scripts, use a process-local execution policy override:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 examples/demo.lox
```

Start the interactive prompt with no arguments:

```powershell
.\run.ps1
```

For example, enter `print 1 + 2 * 3;` to print `7`. You can type or paste functions,
classes, blocks, and expressions over multiple lines. The prompt changes from `>`
to `...` while it waits for the rest of a statement, then executes the complete
submission. Keep semicolons where required: `print counter();`, for example.
Variables and functions persist between submissions.

The interactive prompt highlights Lox keywords, strings, numbers, comments, and
function names as you type. Arrow keys navigate and recall input; Ctrl+C cancels
the current submission, and Ctrl+D on an empty line exits. The launcher downloads
the optional [JLine](https://jline.org/docs/advanced/syntax-highlighting/) 3.30.6
terminal editor into `build/lib` on the first interactive run, verifies its SHA-256
checksum, and reuses it on later runs. That first download needs internet access.
If the editor is unavailable, the prompt uses plain input.

To explicitly use plain input, run `./run.ps1 -Plain`. The `NO_COLOR` environment
variable also disables highlighting. Script output and redirected input remain
plain, so colors never change a program's output.

```text
> class Greeter {
...   greet() {
...     print "Hello, Lox!";
...   }
... }
> Greeter().greet();
Hello, Lox!
```

Type `:cancel` on its own line to discard unfinished input. In plain mode, exit with
Ctrl+Z then Enter on Windows (Ctrl+D on Unix). Exiting with unfinished input reports its syntax
error. For an `if`/`else`, put `else` on the same line as the closing `}` of the
`if` body so the prompt reads both branches as one statement.

## Compile and run manually

No Maven, Gradle, or external Java dependencies are required for the interpreter's
plain prompt or script execution. Run these commands
from the repository root, rather than running `GenerateAst.java` or an individual
source file in the IDE:

```powershell
New-Item -ItemType Directory -Force build/classes | Out-Null
javac -encoding UTF-8 -d build/classes jlox/*.java tool/GenerateAst.java
java -cp build/classes jlox.Lox examples/demo.lox
java -cp build/classes jlox.Lox
```

On macOS/Linux, replace the first line with `mkdir -p build/classes`.
In VS Code, open the repository folder and run the `main` method in `jlox/Lox.java`,
or use the integrated terminal commands above. `jlox.Lox` is the entry point.
Use `run.ps1` to also build and load the optional highlighting editor. VS Code's
Java settings include downloaded jars from `build/lib` on the project classpath.

File execution returns `0` on success, `64` for invalid command-line usage, `65`
for syntax/resolution errors, `70` for Lox runtime errors, and `74` for unreadable
files. Lox source files are read as UTF-8.

## Regression tests

With Python 3 and a JDK on your PATH:

```powershell
py -3 -m unittest discover -s tests -v
```

On macOS/Linux, use `python3 -m unittest discover -s tests -v`. Tests compile fresh
classes in a temporary directory under `build/` and check language behavior, error
exit codes, prompt recovery, the demo output, and compilation after AST regeneration.
No Python packages need to be installed.
Terminal highlighter tests also run if `build/lib/jline-3.30.6.jar` is present;
otherwise those tests are skipped. The interpreter tests always run.

## AST generator

`tool/GenerateAst.java` is a development tool that generates `Expr.java` and
`Stmt.java`; it is not the interpreter entry point. Those files are already checked
in, so regeneration is optional. After compiling:

```text
java -cp build/classes tool.GenerateAst jlox
```

Recompile the interpreter after regenerating the AST.

## Project layout

Java sources and compiled classes are kept in separate folders:

```text
jlox/                   Interpreter source files (.java)
tool/                   AST generator source (.java)
terminal/               Optional terminal editor source (.java)
build/classes/jlox/     Compiled interpreter files (.class)
build/classes/tool/     Compiled AST generator (.class)
build/classes/terminal/ Compiled terminal editor (.class)
build/lib/              Downloaded terminal library (.jar)
examples/               Demo program and expected output
tests/                  Regression tests
```

Both `run.ps1` and the VS Code Java project settings write compiled classes to
`build/classes`. When compiling manually, keep the `-d build/classes` option so
class files stay out of the source folders. Generated classes are ignored by Git.

## C implementation

`clox/` contains an unfinished bytecode VM/scanner implementation from the later
chapters of the book. It does not yet compile or execute Lox source programs. Use
`jlox` for the working interpreter and demo.
