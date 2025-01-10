package jlox;

public class RuntimeError extends RuntimeException {
    final Token token;

    // Constructor
    RuntimeError(Token token, String message) {
        super(message);
        this.token = token;
    }

}
