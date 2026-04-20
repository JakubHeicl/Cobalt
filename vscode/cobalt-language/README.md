# Cobalt VS Code Extension

Minimal VS Code extension scaffold for Cobalt syntax highlighting.

## Included

- `.co` file association
- line comments using `#`
- highlighting for:
  - opcodes
  - labels
  - variables used with `GET` and `SET`
  - jump targets
  - strings
  - numbers
  - experimental keywords such as `FUN`, `CAL`, `RET`, `IMP`, and `IMPORT`

## Local Testing

1. Open the `vscode/cobalt-language` folder in VS Code.
2. Press `F5`.
3. In the new Extension Development Host window, open a `.co` file.
4. If needed, select the language mode `Cobalt`.

## Notes

This is only syntax highlighting. It does not yet provide diagnostics, snippets, autocomplete, or run commands.
