"""Runtime fast path for Open WebUI sqlite chat search, backed by an FTS5 index.

Installed via a .pth file in site-packages so upstream application files are
never modified. The hook only replaces the sqlite branch of
``chat_search_message_content_match_sql`` and steps aside (keeping the stock,
slow implementation) whenever the upstream code or the database schema does
not match what it expects.
"""

import inspect
import os
import sqlite3
import sys
from importlib import machinery
from importlib.abc import MetaPathFinder

TARGET_MODULE = 'open_webui.models.chats'
TARGET_FUNCTION = 'chat_search_message_content_match_sql'
FTS_TABLE = 'chat_message_fts'
FTS_TRIGGER = 'chat_message_fts_ai'
UPSTREAM_SQL_MARKER = 'json_each(Chat.chat'


def _log(message):
    print(f'[fts] {message}', flush=True)


def _sqlite_path():
    """Return the sqlite database path, or None for other backends."""
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


def _fts_available():
    path = _sqlite_path()
    if not path or not os.path.exists(path):
        return False
    try:
        connection = sqlite3.connect(f'file:{path}?mode=ro', uri=True, timeout=2)
        try:
            names = {
                row[0]
                for row in connection.execute(
                    'SELECT name FROM sqlite_master WHERE name IN (?, ?)',
                    (FTS_TABLE, FTS_TRIGGER),
                )
            }
        finally:
            connection.close()
    except Exception as exc:
        _log(f'index check failed: {exc}')
        return False
    return FTS_TABLE in names and FTS_TRIGGER in names


def _match_sql(key):
    return (
        'CASE WHEN length(:{key}) >= 3 THEN '
        'Chat.id IN ('
        'SELECT f.chat_id FROM chat_message_fts f '
        "WHERE f.body MATCH ('\"' || replace(:{key}, '\"', '\"\"') || '\"')"
        ') ELSE '
        'Chat.id IN ('
        'SELECT m.chat_id FROM chat_message m '
        "WHERE m.content LIKE '%' || :{key} || '%'"
        ') END'
    ).format(key=key)


def _apply(module):
    original = getattr(module, TARGET_FUNCTION, None)
    if original is None:
        _log(f'{TARGET_FUNCTION} not found, fast path disabled')
        return
    try:
        source = inspect.getsource(original)
    except Exception:
        source = ''
    if UPSTREAM_SQL_MARKER not in source:
        _log('upstream search implementation changed, fast path disabled')
        return
    if not _fts_available():
        _log(f'{FTS_TABLE} missing, fast path disabled')
        return

    def patched(dialect_name, key):
        if dialect_name == 'sqlite':
            return _match_sql(key)
        return original(dialect_name, key)

    module.chat_search_message_content_match_sql = patched
    _log(f'fast path enabled ({FTS_TABLE})')


class _Finder(MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname != TARGET_MODULE:
            return None
        spec = machinery.PathFinder.find_spec(fullname, path)
        if spec is None or spec.loader is None:
            return None
        original_exec = spec.loader.exec_module

        def exec_module(module):
            original_exec(module)
            try:
                _apply(module)
            except Exception as exc:
                _log(f'fast path failed to apply: {exc}')

        spec.loader.exec_module = exec_module
        return spec


def _install():
    if any(isinstance(finder, _Finder) for finder in sys.meta_path):
        return
    sys.meta_path.insert(0, _Finder())


_install()
