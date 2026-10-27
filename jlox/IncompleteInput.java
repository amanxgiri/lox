package jlox;

// Signals that prompt input needs another line before it can be parsed.
class IncompleteInput extends RuntimeException {
    IncompleteInput() {
        super(null, null, false, false);
    }
}
