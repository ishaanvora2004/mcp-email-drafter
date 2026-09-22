# Structure adapted from the MCP Python SDK README:
# https://github.com/modelcontextprotocol/python-sdk
from datetime import datetime
from pathlib import Path
from dotenv import dotenv_values
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("email-drafter")

# Settings come from the .env file next to this script (not from system variables).
# .env reading pattern from python-dotenv's own documentation:
# https://pypi.org/project/python-dotenv/
BASE_DIR = Path(__file__).parent
config = dotenv_values(BASE_DIR / ".env")
DRAFTS_DIR = BASE_DIR / config.get("DRAFTS_DIR", "drafts")
DRAFTS_DIR.mkdir(exist_ok=True)

def sanitize(text: str) -> str:
    """Removes newline and carriage-return characters so user input cannot
    forge extra header lines (header injection) in the saved draft file."""
    return text.replace("\r", " ").replace("\n", " ")


@mcp.tool()
def write_email_draft(
    recipient_email: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
) -> dict:
    """Saves an email draft as a text file on the user's computer. It does NOT
    send the email.

    Args:
        recipient_email: The recipient's email address.
        subject: The subject line of the email.
        body: The full text of the email, already written out.
        cc: Optional. Email address(es) to copy. Leave empty if none.
        bcc: Optional. Email address(es) to blind-copy. Leave empty if none.

    Use this only when the user asks for an email to be drafted or saved.
    Write the complete email first, then pass it in."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"draft-{timestamp}.txt"
    path = DRAFTS_DIR / filename
    recipient_email = sanitize(recipient_email)
    subject = sanitize(subject)
    cc = sanitize(cc)
    bcc = sanitize(bcc)
    # body is not sanitized: newlines are expected and fine in an email body.

    content = (
        f"TO: {recipient_email}\n"
        f"CC: {cc or '(none)'}\n"
        f"BCC: {bcc or '(none)'}\n"
        f"SUBJECT: {subject}\n"
        f"{'-' * 40}\n"
        f"{body}\n"
    )
    path.write_text(content, encoding="utf-8")
    return {"status": "saved", "filename": filename}


@mcp.tool()
def list_drafts() -> list[dict]:
    """Lists all saved email drafts, newest first. Returns each draft's
    filename, recipient, and subject so the user can skim them quickly.
    Use this when the user asks to see, review, or find their saved drafts.
    """
    results = []
    for path in sorted(DRAFTS_DIR.glob("draft-*.txt"), reverse=True):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            results.append(
                {
                    "filename": path.name,
                    "to": lines[0].removeprefix("TO: "),
                    "subject": lines[3].removeprefix("SUBJECT: "),
                }
            )
        except Exception:
            # Skip unreadable/corrupted files without leaking internal
            # details (file paths, line numbers) back to the caller.
            results.append({"filename": path.name, "error": "Could not read this draft."})
    return results


# Prompt pattern adapted from the MCP Python SDK README:
# https://github.com/modelcontextprotocol/python-sdk
@mcp.prompt()
def professional_email(
    recipient: str,
    purpose: str,
    tone: str = "polite and professional",
    email_trail: str = "",
) -> str:
    """Template for writing a professional email and saving it as a draft."""
    return (
        f"Write an email to {recipient}. Purpose: {purpose}.\n"
        f"Tone: {tone}.\n"
        f"Previous email trail (may be empty):\n{email_trail or '(none provided)'}\n\n"
        "Follow these instructions:\n"
        "1. Begin with 'Hello' and the recipient's name. End with 'Thank you' and a sign-off.\n"
        "2. Keep paragraphs short so the email is easy to skim, and vary how sentences begin instead of repeating 'I'.\n"
        "3. Read the email trail carefully and write a reply that fits the sender's role and responsibilities.\n"
        "4. Do not make assumptions. Mention only facts explicitly stated in the trail or in this request. "
        "If key information is missing, ask the user instead of guessing.\n"
        "5. When the email is ready, save it using the write_email_draft tool. Do NOT send it.\n"
    )


if __name__ == "__main__":
    mcp.run()