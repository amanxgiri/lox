package tests;

import terminal.LoxHighlighter;
import org.jline.utils.AttributedString;
import org.jline.utils.AttributedStyle;

public final class TerminalChecks {
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    public static void main(String[] args) {
        String[] samples = {
            "", "fun makeCounter() {", "var count = 12.5;", "print !false;",
            "// class \"comment\" 42", "print \"a // string\";",
            "print \"unfinished", "print \"first\nsecond\";", "orange or order",
            "fun f() {\n  return 1;\n}", "print \"hello λ\";"
        };
        for (String sample : samples) {
            check(LoxHighlighter.colorize(sample).toString().equals(sample), "Changed source: " + sample);
        }

        AttributedString code = LoxHighlighter.colorize("var count = 12.5; // return 2");
        check(!code.styleAt(0).equals(AttributedStyle.DEFAULT), "Keyword has no color");
        check(code.styleAt(4).equals(AttributedStyle.DEFAULT), "Variable should retain default style");
        check(!code.styleAt(12).equals(code.styleAt(0)), "Numbers and keywords need distinct colors");
        check(code.styleAt(12).equals(code.styleAt(15)), "Decimal number lost its style");
        check(code.styleAt(18).equals(code.styleAt(22)), "Keywords inside comments should stay comments");

        AttributedString string = LoxHighlighter.colorize("\"class // 42\"");
        check(string.styleAt(0).equals(string.styleAt(4)), "Keyword inside string was recolored");
        check(string.styleAt(0).equals(string.styleAt(8)), "Comment inside string was recolored");
        AttributedString identifiers = LoxHighlighter.colorize("orange or falsehood");
        check(identifiers.styleAt(0).equals(AttributedStyle.DEFAULT), "Identifier prefix matched keyword");
        check(!identifiers.styleAt(7).equals(AttributedStyle.DEFAULT), "Logical keyword has no color");
        check(identifiers.styleAt(10).equals(AttributedStyle.DEFAULT), "Keyword prefix matched identifier");

        LoxHighlighter highlighter = new LoxHighlighter();
        highlighter.setPending("print \"first\n");
        AttributedString continued = highlighter.highlight(null, "second\";");
        check(continued.toString().equals("second\";"), "Previous input leaked into current line");
        check(continued.styleAt(0).equals(string.styleAt(0)), "Multiline string lost its color");
        check(continued.styleAt(7).equals(AttributedStyle.DEFAULT), "String style leaked past quote");
        highlighter.setPending("");
        check(highlighter.highlight(null, "var x;").styleAt(0).equals(code.styleAt(0)), "State did not reset");
        check(code.toAnsi().contains("\u001b["), "No ANSI colors generated");
        System.out.println("Terminal highlighting checks passed.");
    }
}
