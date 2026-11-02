# Privacy and publication policy

This repository is safe to publish only when it contains implementation,
schemas, generic benchmark prompts, and sanitized aggregate records.

Never publish:

- OpenCode SQLite databases or WAL files.
- Raw prompts, assistant content, tool inputs, or tool outputs.
- Session, message, part, call, T3 thread, or pull-request identifiers.
- API keys, tokens, credentials, cookies, private paths, or personal notes.
- Generated audit bundles, local stores, or experiment data containing raw context.

The local collector may inspect these data sources, but the repository is not a
data export. Generated local output belongs in ignored directories.
