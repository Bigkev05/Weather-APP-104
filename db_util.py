import sqlite3

def open_db( database_name: str ) -> sqlite3.Cursor:
    '''
    Opens a SQLite databse specified by file name.

    Parameters:
    database_name (str) - the name of the databse file

    Returns:
    A Cursor which can be used to interact with the database
    '''
    connection = sqlite3.connect(database = database_name)
    cursor = connection.cursor()
    return cursor

def close_db( cursor: sqlite3.Cursor ) -> None:
    '''
    Closes cursor and associated connection
    '''
    cursor.close()
    cursor.connection.close()
