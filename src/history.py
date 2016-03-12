# coding=utf-8
import sqlite3
from settings import Settings
import os


MESSAGE_OWNER = {
    'ME': 0,
    'FRIEND': 1
}


class History(object):
    def __init__(self, name):
        self._name = name
        os.chdir(Settings.get_default_path())
        db = sqlite3.connect(name + '.hstr')
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS friends('
                       '    tox_id TEXT PRIMARY KEY'
                       ')')
        db.close()

    def add_friend_to_db(self, tox_id):
        os.chdir(Settings.get_default_path())
        db = sqlite3.connect(self._name + '.hstr')
        try:
            cursor = db.cursor()
            cursor.execute('INSERT INTO friends VALUES (?);', (tox_id, ))
            cursor.execute('CREATE TABLE id' + tox_id + '('
                           '    id INTEGER PRIMARY KEY,'
                           '    message TEXT,'
                           '    owner INTEGER,'
                           '    unix_time INTEGER'
                           '    message_type INTEGER'
                           ')')
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_friend_from_db(self, tox_id):
        os.chdir(Settings.get_default_path())
        db = sqlite3.connect(self._name + '.hstr')
        try:
            cursor = db.cursor()
            cursor.execute('DELETE FROM friends WHERE tox_id=?;', (tox_id, ))
            cursor.execute('DROP TABLE id' + tox_id + ';')
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def friend_exists_in_db(self, tox_id):
        os.chdir(Settings.get_default_path())
        db = sqlite3.connect(self._name + '.hstr')
        cursor = db.cursor()
        cursor.execute('SELECT 0 FROM friends WHERE tox_id=?', (tox_id, ))
        result = cursor.fetchone()
        db.close()
        return result is not None

    def save_messages_to_db(self, tox_id, messages_iter):
        os.chdir(Settings.get_default_path())
        db = sqlite3.connect(self._name + '.hstr')
        try:
            cursor = db.cursor()
            cursor.executemany('INSERT INTO id' + tox_id + '(message, owner, unix_time) '
                               'VALUES (?, ?, ?);', messages_iter)
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def messages_getter(self, tox_id):
        return History.MessageGetter(self._name, tox_id)

    class MessageGetter(object):
        def __init__(self, name, tox_id):
            os.chdir(Settings.get_default_path())
            self._db = sqlite3.connect(name + '.hstr')
            self._cursor = self._db.cursor()
            self._cursor.execute('SELECT message, owner, unix_time FROM id' + tox_id +
                                 ' ORDER BY unix_time DESC;')

        def get_one(self):
            return self._cursor.fetchone()

        def get_all(self):
            return self._cursor.fetchall()

        def get(self, count):
            return self._cursor.fetchmany(count)

        def __del__(self):
            self._db.close()


if __name__ == '__main__':
    h = History('test')
    getter = h.messages_getter('42')
    print h.friend_exists_in_db('42'), type(h.friend_exists_in_db('42'))