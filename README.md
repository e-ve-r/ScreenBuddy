# Local browser research → Apple Notes

The default engine opens a dedicated Google Chrome profile, reads the page DOM,
follows extracted links, visits relevant articles, and saves cited findings to
Apple Notes. Llama 3.2 selects links and passages; findings are taken directly
from retrieved paragraphs. The report is an extractive brief, not a model essay.

## Run

```bash
cd /Users/ever/Documents/ChatGPT/Vision
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python computer_use_gui.py
```

Close and reopen old GUI windows to load updates. Choose **Custom browser task**,
enter `go to bbc and look for latest international news`, and click **Run task**.
The GUI includes models, timeouts, visit budget, source-article count, output paths,
and an optional website URL for unfamiliar sites.

**Attach page images** adds a screenshot of each selected source page to Notes.
These are labelled browser captures, not original publisher photographs. Captions
and image alt text are included where available.

## CLI

```bash
.venv/bin/python computer_use_agent.py \
  --task "go to bbc and look for latest international news" \
  --max-pages 4 --max-steps 15 --include-images
```

Use `--start-url https://example.com/topic` to choose an explicit destination.
BBC, Reuters, CNN, Wikipedia and LinkedIn have built-in destination aliases.
Requests without a recognized site start with a web search.

`--no-notes` saves files only; `--headless` hides the research browser.

When the browser encounters a recognizable verification challenge, it waits up to
five minutes for you to complete it. Use `--verification-timeout 600` to change
the wait to ten minutes. Verification requires a visible browser, so do not use
`--headless` when you need to complete a challenge.
`--dry-run` prints the initial destination without browsing or creating a note.
The old Moondream/PyAutoGUI loop is available with `--engine visual`; its coordinate
clicks and screenshot-only findings are less reliable. The GUI uses the browser engine.

## Browser and models

Playwright uses your installed Google Chrome, so no extra Chromium download is
needed. The dedicated profile lives at `artifacts/chrome-research-profile`.
It does not reuse your everyday Chrome login. Login walls, CAPTCHAs and inaccessible
pages can block a task. This engine follows ordinary links and reads pages; it
does not submit job applications or perform arbitrary account actions.

Start Ollama and ensure `llama3.2:latest` is installed. Moondream is used by the
optional visual engine, not by DOM research.

```bash
ollama serve
# In another terminal if the model is missing:
ollama pull llama3.2:latest
```

## Notes and completion

Allow the launching app to control Notes when macOS requests Automation access.
Notes is written through AppleScript. The saved full text and attachment count
are checked before success is reported; no simulated Command+V is involved.
The visual engine additionally requires Accessibility and Screen Recording access.

- `artifacts/browser_output.txt`: cited findings with publication and retrieval dates.
- `artifacts/screenshots/research-*/`: retrieved text/link snapshots, screenshots,
  and a `research.json` audit record in a new directory for each run.
- `artifacts/run_status.json`: progress and outcome displayed by the GUI.

Use Stop or Ctrl+C to interrupt. If no relevant source text can be read, the run
fails and saves diagnostics rather than fabricating findings. macOS notifications
are best-effort; terminal and GUI status also show the outcome.

A completed brief means retrieved sources were saved, not that every relevant
story was covered. Small models can choose irrelevant articles; the links and
exact source passages make that checkable. Dates come from publishers. Increase
the visit budget or specify a topic-section URL for a more focused request.

Regression tests: `.venv/bin/python -m unittest -v`.
