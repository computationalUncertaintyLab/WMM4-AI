"""
Weekly public health communications: one folder per release (comm1, comm2, …).

Each folder may use either:
  - public_health_communication.md with ## Social media, ## Brief communication, ## Detailed communication
  - or separate files: social_media_post.md, brief_communication.md, learn_more.txt

"Learn more" downloads a styled HTML document (Markdown in the source is converted for bold, lists, etc.).

Optional posted_date.txt (first line only): if present, that text is shown as the post date instead of
the source file's creation time.
"""
import html
import re
from datetime import datetime
from pathlib import Path

import markdown
import streamlit as st

COMM_ROOT = Path(__file__).resolve().parent / "communications"


def _comm_sort_key(name: str) -> tuple:
    m = re.fullmatch(r"comm(\d+)", name, re.IGNORECASE)
    if m:
        return (0, int(m.group(1)))
    return (1, name.lower())


def _list_comm_dirs() -> list[str]:
    if not COMM_ROOT.is_dir():
        return []
    names = [
        p.name
        for p in COMM_ROOT.iterdir()
        if p.is_dir() and p.name.lower().startswith("comm")
    ]
    return sorted(names, key=_comm_sort_key)


def _split_md_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_key: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_key is not None:
                sections[current_key] = "\n".join(buf).strip()
            current_key = line[3:].strip().lower()
            buf = []
        else:
            buf.append(line)
    if current_key is not None:
        sections[current_key] = "\n".join(buf).strip()
    return sections


def _format_date_from_source_file(path: Path) -> str:
    """Human-readable date from file creation time (birthtime if OS provides it, else mtime)."""
    st = path.stat()
    ts = getattr(st, "st_birthtime", None)
    if ts is None:
        ts = st.st_mtime
    dt = datetime.fromtimestamp(ts)
    return f"{dt.strftime('%A, %B')} {dt.day}, {dt.year}"


def _detailed_communication_html(
    *,
    document_title: str,
    posted_on: str,
    body_md: str,
) -> str:
    """Self-contained HTML with typography suited for reading and printing."""
    inner = markdown.markdown(
        body_md.strip(),
        extensions=["extra", "sane_lists", "nl2br"],
    )
    posted_html = ""
    if posted_on:
        posted_html = (
            f'<p class="posted-line"><strong>Posted:</strong> '
            f"{html.escape(posted_on)}</p>"
        )
    safe_title = html.escape(document_title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    :root {{
      --bg: #f7f9fc;
      --paper: #ffffff;
      --text: #1a1d26;
      --muted: #5c6578;
      --accent: #0d6efd;
      --rule: #e2e8f0;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", system-ui, -apple-system, Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 1.05rem;
      line-height: 1.65;
      color: var(--text);
      background: var(--bg);
    }}
    .wrap {{
      max-width: 40rem;
      margin: 0 auto;
      padding: 2rem 1.5rem 3rem;
    }}
    header {{
      background: var(--paper);
      border: 1px solid var(--rule);
      border-radius: 12px;
      padding: 1.5rem 1.75rem;
      margin-bottom: 1.75rem;
      box-shadow: 0 1px 3px rgba(0,0,0,.06);
    }}
    header h1 {{
      margin: 0 0 0.35rem 0;
      font-size: 1.35rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text);
    }}
    header .subtitle {{
      margin: 0;
      font-size: 0.95rem;
      color: var(--muted);
    }}
    .posted-line {{
      margin: 1rem 0 0 0;
      font-size: 0.95rem;
      color: var(--muted);
      padding-top: 0.75rem;
      border-top: 1px solid var(--rule);
    }}
    .posted-line strong {{ color: var(--text); }}
    main {{
      background: var(--paper);
      border: 1px solid var(--rule);
      border-radius: 12px;
      padding: 1.75rem 1.75rem 2rem;
      box-shadow: 0 1px 3px rgba(0,0,0,.06);
    }}
    main h1, main h2, main h3 {{
      margin-top: 1.25rem;
      margin-bottom: 0.5rem;
      line-height: 1.3;
      color: var(--text);
    }}
    main h2 {{ font-size: 1.15rem; border-bottom: 2px solid var(--accent); padding-bottom: 0.2rem; }}
    main p {{ margin: 0.75rem 0; }}
    main ul, main ol {{ margin: 0.5rem 0 0.75rem 1.25rem; padding-left: 0.25rem; }}
    main li {{ margin: 0.35rem 0; }}
    main strong {{ color: #111827; }}
    main a {{ color: var(--accent); }}
    footer {{
      margin-top: 2rem;
      text-align: center;
      font-size: 0.85rem;
      color: var(--muted);
    }}
    @media print {{
      body {{ background: #fff; }}
      .wrap {{ max-width: none; padding: 0; }}
      header, main {{ box-shadow: none; border-radius: 0; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Detailed communication</h1>
      <p class="subtitle">Watermelon Meow Meow (WMM) — public health communication</p>
      {posted_html}
    </header>
    <main class="content">
      {inner}
    </main>
    <footer>
      <p>{safe_title}</p>
    </footer>
  </div>
</body>
</html>
"""


def _load_post(comm_path: Path) -> dict[str, str] | None:
    md_path = comm_path / "public_health_communication.md"
    social_path = comm_path / "social_media_post.md"
    brief_path = comm_path / "brief_communication.md"
    learn_path = comm_path / "learn_more.txt"

    social = brief = detailed = ""

    if md_path.is_file():
        sec = _split_md_sections(md_path.read_text(encoding="utf-8"))
        social = sec.get("social media", "").strip()
        brief = sec.get("brief communication", "").strip()
        detailed = sec.get("detailed communication", "").strip()
    elif social_path.is_file() and brief_path.is_file() and learn_path.is_file():
        social = social_path.read_text(encoding="utf-8").strip()
        brief = brief_path.read_text(encoding="utf-8").strip()
        detailed = learn_path.read_text(encoding="utf-8").strip()
    else:
        return None

    if social_path.is_file() and not social:
        social = social_path.read_text(encoding="utf-8").strip()
    if brief_path.is_file() and not brief:
        brief = brief_path.read_text(encoding="utf-8").strip()
    if learn_path.is_file() and not detailed:
        detailed = learn_path.read_text(encoding="utf-8").strip()

    if not social:
        return None

    anchor = md_path if md_path.is_file() else social_path
    override = comm_path / "posted_date.txt"
    if override.is_file():
        first = override.read_text(encoding="utf-8").strip().splitlines()
        posted_on = first[0].strip() if first else ""
        if not posted_on and anchor.is_file():
            posted_on = _format_date_from_source_file(anchor)
    else:
        posted_on = _format_date_from_source_file(anchor) if anchor.is_file() else ""

    return {
        "folder": comm_path.name,
        "social": social,
        "brief": brief,
        "detailed": detailed,
        "posted_on": posted_on,
    }


def show() -> None:
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("🚫 You must log in first.")
        st.stop()

    st.title("Public health communication of WMM")
    st.caption("Watermelon Meow Meow (WMM)")

    dirs = _list_comm_dirs()
    if not dirs:
        st.info("No communications have been published yet. Add folders such as `comm1`, `comm2`, … under `pages/communications/`.")
        return

    for idx, d in enumerate(dirs):
        post = _load_post(COMM_ROOT / d)
        if post is None:
            st.warning(
                f"**{d}** is missing a valid bundle. Add `public_health_communication.md` "
                "with sections **Social media**, **Brief communication**, and **Detailed communication**, "
                "or add `social_media_post.md`, `brief_communication.md`, and `learn_more.txt`."
            )
            continue

        posted_on = (post.get("posted_on") or "").strip()
        social_label = (
            f"**Posted: {posted_on}**\n\n{post['social']}"
            if posted_on
            else post["social"]
        )
        with st.expander(social_label, expanded=False):
            if post["brief"]:
                brief_md = (
                    f"**Posted: {posted_on}**\n\n{post['brief']}"
                    if posted_on
                    else post["brief"]
                )
                st.markdown(brief_md)
            else:
                if posted_on:
                    st.markdown(f"**Posted: {posted_on}**")
                st.caption("No brief communication for this post.")

            detailed = post["detailed"]
            if detailed:
                safe_name = re.sub(r"[^\w\-]+", "_", post["folder"])
                doc_title = f"WMM {post['folder']} — detailed communication"
                html_doc = _detailed_communication_html(
                    document_title=doc_title,
                    posted_on=posted_on,
                    body_md=detailed,
                )
                st.download_button(
                    "Learn more",
                    data=html_doc.encode("utf-8"),
                    file_name=f"WMM_{safe_name}_detailed_communication.html",
                    mime="text/html",
                    key=f"learn_more_{post['folder']}_{idx}",
                )
            else:
                st.caption("Extended document is not available for this post.")


if __name__ == "__main__":
    show()
