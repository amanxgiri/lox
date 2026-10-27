package jlox;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

public class Lox {

    private static final Interpreter interpreter = new Interpreter();

    static boolean hadError = false;
    static boolean hadRuntimeError = false;

    public static void main(String[] args) throws IOException {
        if (args.length > 1) {
            System.out.println("Usage: jlox [script]");
            System.exit(64);
        } else if (args.length == 1) {
            try {
                runFile(args[0]);
            } catch (IOException error) {
                System.err.println("Could not read file '" + args[0] + "': " + error.getMessage());
                System.exit(74);
            }
        } else {
            runPrompt();
        }

    }

    private static void runFile(String path) throws IOException {
        byte[] bytes = Files.readAllBytes(Paths.get(path));
        run(new String(bytes, StandardCharsets.UTF_8));

        // Indicate an Error in the exit code.
        if (hadError) {
            System.exit(65);
        }
        if (hadRuntimeError) {
            System.exit(70);
        }

    }

    private static void runPrompt() throws IOException {
        try (Prompt input = Prompt.open()) {
            runPrompt(input);
        }
    }

    private static void runPrompt(Prompt input) throws IOException {
        StringBuilder source = new StringBuilder();

        for (;;) {
            String line = input.readLine(source.length() == 0 ? "> " : "... ", source.toString());
            if (line == null) {
                // Report an unfinished submission when input ends.
                if (source.length() > 0) {
                    run(source.toString());
                }
                break;
            }
            if (line.trim().equals(":cancel")) {
                source.setLength(0);
                continue;
            }

            source.append(line).append('\n');
            try {
                run(source.toString(), true);
            } catch (IncompleteInput incomplete) {
                continue;
            }

            source.setLength(0);
            hadError = false;
            hadRuntimeError = false;
        }
    }

    private static void run(String source) {
        run(source, false);
    }

    private static void run(String source, boolean allowIncomplete) {
        Scanner scanner = new Scanner(source, allowIncomplete);
        List<Token> tokens = scanner.scanTokens();
        if (hadError) {
            return;
        }

        Parser parser = new Parser(tokens, allowIncomplete);
        List<Stmt> statements = parser.parse();

        // Stop if there was a syntax error.
        if (hadError) {
            return;
        }

        Resolver resolver = new Resolver(interpreter);
        resolver.resolve(statements);
        if (hadError) {
            return;
        }

        interpreter.interpret(statements);
    }

    static void error(int line, String message) {
        report(line, "", message);
    }

    static void runtimeError(RuntimeError error) {
        System.err.println(error.getMessage() + "\n[line " + error.token.line + "]");
        hadRuntimeError = true;
    }

    private static void report(int line, String where, String message) {
        System.err.println("[line " + line + "] Error" + where + ": " + message);
        hadError = true;
    }

    static void error(Token token, String message) {
        if (token.type == TokenType.EOF) {
            report(token.line, " at end", message);
        } else {
            report(token.line, "  at   '" + token.lexeme + "'", message);
        }
    }

}
