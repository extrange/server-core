# Custom Open WebUI image adding an FTS5 fast path for sqlite chat search.
# See fts_hook.py (runtime monkeypatch) and fts_migrate.py (index maintenance).
# The base digest is intentionally pinned; Renovate tracks it in this file.
FROM ghcr.io/open-webui/open-webui:cuda@sha256:19d67779c48057ccfc8f133ec9585995e1e1c200498ed3444706df2961f2c7a9

COPY fts_hook.py /usr/local/lib/python3.11/site-packages/fts_hook.py
COPY fts_hook.pth /usr/local/lib/python3.11/site-packages/zz_open_webui_fts.pth
COPY fts_migrate.py /app/backend/fts_migrate.py

# Build the search index before the app starts; the migrate script never fails
# the boot, so the image is safe even when indexing is skipped.
CMD ["bash", "-c", "python3 /app/backend/fts_migrate.py; exec bash start.sh"]
