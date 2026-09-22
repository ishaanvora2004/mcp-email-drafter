# Email Drafter MCP Server

I'm a Chemical Engineer and this is my first time building anything
with AI tooling or a software protocol like MCP. This project is a small MCP
(Model Context Protocol) server that lets Claude draft and save emails on my
behalf, without ever sending them. I built it for Applied AI for Technical
Teams to learn how MCP servers work and how to connect one to an AI client.

## Domain
Personal Productivity

## Tools
- `write_email_draft` — Saves an email draft (recipient, subject, body, and
  optional CC/BCC) as a labeled text file on disk. It does not send anything.
- `list_drafts` — Reads every saved draft and returns its filename, recipient,
  and subject, newest first, so drafts are easy to skim.

## Prompt
- `professional_email` — A reusable template that takes a recipient, purpose,
  and tone, and turns them into a full set of writing instructions for Claude
  (structure, tone, no unsupported assumptions, and saving the result with
  `write_email_draft` instead of sending it).

## Setup

1. Clone this repository.
2. Create a virtual environment and activate it (using `uv`):
   ```
   uv venv
   .venv\Scripts\activate
   ```
   (On Mac/Linux: `source .venv/bin/activate`)
3. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and adjust if needed:
   ```
   copy .env.example .env
   ```
   (On Mac/Linux: `cp .env.example .env`)
5. Run the server directly (optional, for testing without Claude Desktop):
   ```
   python server.py
   ```
   The terminal will sit with no output while it's running, that means it's
   working, and is waiting for a client to connect. Press Ctrl+C to stop it.

## Connecting to Claude Desktop

Open Claude Desktop's config file (Settings → Developer → Edit Config, or
directly at `%APPDATA%\Claude\claude_desktop_config.json` on Windows) and add
this server under `mcpServers`:

```json
{
  "mcpServers": {
    "email-drafter": {
      "command": "<your-path>\\.venv\\Scripts\\python.exe",
      "args": ["<your-path>\\server.py"]
    }
  }
}
```

Replace `<your-path>` with the full path to this project folder on your own
machine. Fully quit and reopen Claude Desktop afterward (closing the window
isn't enough, the app keeps running in the background), then check
Settings → Developer to confirm the server shows as "Running."

## Best Practices Implemented

1. **Input Sanitization** — `write_email_draft` strips newline and carriage
   return characters from the recipient, subject, CC, and BCC fields before
   writing them to the draft file. Without this, someone could put a newline
   followed by fake header text (e.g. `Subject\nBCC: attacker@evil.com`) into
   the subject field, and it would show up in the saved file looking like a
   real BCC line even though it never came through the real `bcc` input. This
   is a header injection attack, a known risk with any code that writes
   user-supplied text into a labeled, line-based format. The body field is
   left alone on purpose, since a normal email body is expected to have
   multiple lines.

2. **Error Disclosure** — `list_drafts` wraps the part of the code that reads
   and parses each saved file in a try/except block. If a file is
   corrupted or unreadable, the tool used to crash and return a full Python
   traceback, including the exact file path on my computer and the internal
   line of code that failed. That's useful for me while developing, but
   handing it back to an AI client or an end user leaks details about my
   file system for no real benefit. Now a bad file just gets marked with a
   short, generic message ("Could not read this draft.") and the tool keeps
   going instead of failing completely.

## Security Note

This version saves drafts locally and doesn't call any external service, so
there's no real API key to protect yet. I still built the `.env` /
`.env.example` pattern in from the start, because it's the right place to add
a real credential (for example, a Gmail API key) if I extend this to create
drafts in an actual email account, without ever committing that secret to
GitHub.
