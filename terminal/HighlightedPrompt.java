package terminal;

import java.io.IOException;

import jlox.Prompt;
import org.jline.reader.EndOfFileException;
import org.jline.reader.LineReader;
import org.jline.reader.LineReaderBuilder;
import org.jline.reader.UserInterruptException;
import org.jline.reader.impl.DefaultParser;
import org.jline.terminal.Terminal;
import org.jline.terminal.TerminalBuilder;

public final class HighlightedPrompt implements Prompt {
    private final Terminal terminal;
    private final LineReader reader;
    private final LoxHighlighter highlighter = new LoxHighlighter();

    public HighlightedPrompt() throws IOException {
        terminal = TerminalBuilder.builder().system(true).dumb(false).build();
        // Lox, rather than the shell parser, decides when a submission is complete.
        DefaultParser parser = new DefaultParser()
                .quoteChars(new char[0]).escapeChars(new char[0])
                .eofOnEscapedNewLine(false);
        reader = LineReaderBuilder.builder().terminal(terminal).appName("lox")
                .parser(parser).highlighter(highlighter)
                .option(LineReader.Option.DISABLE_EVENT_EXPANSION, true).build();
    }

    @Override
    public String readLine(String prompt, String pending) {
        highlighter.setPending(pending);
        try {
            return reader.readLine(prompt);
        } catch (UserInterruptException cancelled) {
            return ":cancel";
        } catch (EndOfFileException end) {
            return null;
        }
    }

    @Override
    public void close() throws IOException {
        terminal.close();
    }
}
