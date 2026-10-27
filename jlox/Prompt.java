package jlox;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

// The interpreter can run without the optional terminal editor on its classpath.
public interface Prompt extends AutoCloseable {
    String readLine(String prompt, String pending) throws IOException;

    @Override
    void close() throws IOException;

    static Prompt open() {
        if (isTerminal() && System.getenv("NO_COLOR") == null
                && !Boolean.getBoolean("lox.noColor")) {
            try {
                return (Prompt) Class.forName("terminal.HighlightedPrompt")
                        .getDeclaredConstructor().newInstance();
            } catch (ClassNotFoundException unavailable) {
                // A core-only build uses the standard input reader below.
            } catch (ReflectiveOperationException | LinkageError unavailable) {
                System.err.println("Live highlighting unavailable; using plain input.");
            }
        }

        final BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        return new Prompt() {
            @Override
            public String readLine(String prompt, String pending) throws IOException {
                System.out.print(prompt);
                System.out.flush();
                return reader.readLine();
            }

            @Override
            public void close() {
                // Standard input belongs to the process.
            }
        };
    }

    static boolean isTerminal() {
        if (System.console() == null) return false;
        try {
            // New JDKs can return a Console even when standard input is redirected.
            return (Boolean) java.io.Console.class.getMethod("isTerminal").invoke(System.console());
        } catch (NoSuchMethodException olderJdk) {
            return true;
        } catch (ReflectiveOperationException unavailable) {
            return false;
        }
    }
}
