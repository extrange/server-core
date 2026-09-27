"""Create and maintain the FTS5 trigram index used by the patched sqlite chat search.

Runs before the application starts. Idempotent and never exits non-zero: when
anything goes wrong the import hook simply does not enable the fast path and
the stock search implementation is used.
"""

import os
import sqlite3
import time

FTS_TABLE = 'chat_message_fts'
META_TABLE = 'chat_message_fts_meta'
BACKFILL_KEY = 'backfilled'

CREATE_FTS = f"""
CREATE VIRTUAL TABLE IF NOT EXISTS {FTS_TABLE}
USING fts5(body, chat_id UNINDEXED, tokenize='trigram')
"""

CREATE_META = f"""
CREATE TABLE IF NOT EXISTS {META_TABLE} (k TEXT PRIMARY KEY, v TEXT)
"""

CREATE_TRIGGERS = f"""
CREATE TRIGGER IF NOT EXISTS {FTS_TABLE}_ai AFTER INSERT ON chat_message
WHEN new.done = 1
BEGIN
    INSERT INTO {FTS_TABLE}(rowid, body, chat_id)
    VALUES (new.rowid, COALESCE(json_extract(new.content, '$'), ''), new.chat_id);
END;

CREATE TRIGGER IF NOT EXISTS {FTS_TABLE}_au AFTER UPDATE ON chat_message
WHEN new.done = 1 AND (old.done IS NOT 1 OR old.content IS NOT new.content)
BEGIN
    DELETE FROM {FTS_TABLE} WHERE rowid = old.rowid;
    INSERT INTO {FTS_TABLE}(rowid, body, chat_id)
    VALUES (new.rowid, COALESCE(json_extract(new.content, '$'), ''), new.chat_id);
END;

CREATE TRIGGER IF NOT EXISTS {FTS_TABLE}_ad AFTER DELETE ON chat_message
BEGIN
    DELETE FROM {FTS_TABLE} WHERE rowid = old.rowid;
END;
"""


def db_path():
    url = os.environ.get('DATABASE_URL') or ''
    if not url:
        return os.path.join(os.environ.get('DATA_DIR') or '/app/backend/data', 'webui.db')
    if not url.startswith('sqlite') or 'sqlcipher' in url:
        return None
    for sep in (':///', '://'):
        if sep in url:
            path = url.split(sep, 1)[1]
            break
    else:
        return None
    return path.split('?', 1)[0] or None


def main():
    path = db_path()
    if path is None:
        print('[fts] not a plain sqlite database; indexing skipped', flush=True)
        return
    if not os.path.exists(path):
        print(f'[fts] database not found at {path}; indexing skipped', flush=True)
        return

    started = time.time()
    connection = sqlite3.connect(path, timeout=30)
    try:
        connection.execute('PRAGMA busy_timeout = 30000')
        connection.execute(CREATE_FTS)
        connection.execute(CREATE_META)

        has_messages = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'chat_message'"
        ).fetchone()
        if not has_messages:
            connection.commit()
            print('[fts] chat_message table not present yet; index will be built on next start', flush=True)
            return

        connection.executescript(CREATE_TRIGGERS)

        marker = connection.execute(
            f'SELECT v FROM {META_TABLE} WHERE k = ?', (BACKFILL_KEY,)
        ).fetchone()
        if marker is None:
            expected = connection.execute(
                'SELECT COUNT(*) FROM chat_message WHERE content IS NOT NULL'
            ).fetchone()[0]
            print(f'[fts] building index over {expected} messages...', flush=True)
            connection.execute(f'DELETE FROM {FTS_TABLE}')
            connection.execute(
                f"""
                INSERT INTO {FTS_TABLE}(rowid, body, chat_id)
                SELECT rowid, COALESCE(json_extract(content, '$'), ''), chat_id
                FROM chat_message
                WHERE content IS NOT NULL
                """
            )
            connection.execute(
                f'INSERT OR REPLACE INTO {META_TABLE}(k, v) VALUES (?, ?)',
                (BACKFILL_KEY, str(int(time.time()))),
            )
            connection.commit()

        indexed = connection.execute(f'SELECT COUNT(*) FROM {FTS_TABLE}').fetchone()[0]
        print(f'[fts] ready: {indexed} messages indexed in {time.time() - started:.1f}s', flush=True)
    finally:
        connection.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'[fts] indexing skipped: {exc}', flush=True)
