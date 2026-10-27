package terminal;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import org.jline.reader.Highlighter;
import org.jline.reader.LineReader;
import org.jline.utils.AttributedString;
import org.jline.utils.AttributedStringBuilder;
import org.jline.utils.AttributedStyle;

public final class LoxHighlighter implements Highlighter {
    private static final Set<String> KEYWORDS = new HashSet<>(Arrays.asList(
            "and", "class", "else", "false", "for", "fun", "if", "nil", "or",
            "print", "return", "super", "this", "true", "var", "while"));
    private static final AttributedStyle KEYWORD = AttributedStyle.DEFAULT
            .foreground(AttributedStyle.MAGENTA).bold();
    private static final AttributedStyle STRING = AttributedStyle.DEFAULT.foreground(AttributedStyle.GREEN);
    private static final AttributedStyle NUMBER = AttributedStyle.DEFAULT.foreground(AttributedStyle.CYAN);
    private static final AttributedStyle COMMENT = AttributedStyle.DEFAULT
            .foreground(AttributedStyle.BLACK + AttributedStyle.BRIGHT);
    private static final AttributedStyle FUNCTION = AttributedStyle.DEFAULT.foreground(AttributedStyle.YELLOW);
    private String pending = "";

    public void setPending(String pending) {
        this.pending = pending;
    }

    @Override
    public AttributedString highlight(LineReader reader, String buffer) {
        // Previous lines matter when the user is still inside a multiline string.
        AttributedString text = colorize(pending + buffer);
        return text.subSequence(pending.length(), text.length());
    }

    public static AttributedString colorize(String source) {
        AttributedStringBuilder result = new AttributedStringBuilder();
        int current = 0;
        while (current < source.length()) {
            int start = current;
            char c = source.charAt(current++);
            AttributedStyle style = AttributedStyle.DEFAULT;
            if (c == '/' && current < source.length() && source.charAt(current) == '/') {
                while (current < source.length() && source.charAt(current) != '\n') current++;
                style = COMMENT;
            } else if (c == '"') {
                while (current < source.length() && source.charAt(current) != '"') current++;
                if (current < source.length()) current++;
                style = STRING;
            } else if (isDigit(c)) {
                while (current < source.length() && isDigit(source.charAt(current))) current++;
                if (current + 1 < source.length() && source.charAt(current) == '.'
                        && isDigit(source.charAt(current + 1))) {
                    current++;
                    while (current < source.length() && isDigit(source.charAt(current))) current++;
                }
                style = NUMBER;
            } else if (isAlpha(c)) {
                while (current < source.length()
                        && (isAlpha(source.charAt(current)) || isDigit(source.charAt(current)))) current++;
                if (KEYWORDS.contains(source.substring(start, current))) {
                    style = KEYWORD;
                } else {
                    int next = current;
                    while (next < source.length() && Character.isWhitespace(source.charAt(next))) next++;
                    if (next < source.length() && source.charAt(next) == '(') style = FUNCTION;
                }
            }
            result.style(style).append(source, start, current);
        }
        return result.toAttributedString();
    }

    private static boolean isDigit(char c) {
        return c >= '0' && c <= '9';
    }

    private static boolean isAlpha(char c) {
        return c >= 'a' && c <= 'z' || c >= 'A' && c <= 'Z' || c == '_';
    }
}
