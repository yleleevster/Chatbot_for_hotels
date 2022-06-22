import config_data.config
import sqlite3 as sq
from typing import Union


def data_collection() -> None:
    """ First step create database and related tables """
    with sq.connect(config_data.config.data_base) as con:
        cur = con.cursor()
        cur.execute(""" CREATE TABLE IF NOT EXISTS states(
           chat_id TEXT,
           state TEXT
           ); """)
        cur.execute(""" CREATE TABLE IF NOT EXISTS history(
               id INTEGER PRIMARY KEY autoincrement,
               uid TEXT,
               chat_id TEXT,
               date_time TEXT,
               city TEXT,
               check_in TEXT,
               check_out TEXT,
               quantity TEXT,
               quantity_photos TEXT,
               Error BOOLEAN,
               commands TEXT,
               price_min TEXT,
               price_max TEXT,
               distance TEXT,
               period TEXT);
             """)
        cur.execute(""" CREATE TABLE IF NOT EXISTS hotels(
                       id INTEGER PRIMARY KEY autoincrement,
                       uid TEXT,
                       hotel_id TEXT,
                       name TEXT,
                       adress TEXT,
                       center TEXT,
                       price TEXT,
                       coordinates TEXT,
                       star_rating TEXT,
                       user_rating TEXT);
                    """)
        cur.execute("""CREATE TABLE IF NOT EXISTS photos(
                         id INTEGER PRIMARY KEY autoincrement,
                         hotel_id TEXT,
                         photo TEXT);
                     """)
        # cur.execute(""" DROP TABLE IF EXISTS _""")


def get_database(string: str) -> list:
    """ Second step get database from the table according to API access """
    with sq.connect(config_data.config.data_base) as con:
        cur = con.cursor()
        cur.execute(string)
        return cur.fetchall()


def delete_table(*args) -> None:
    """ Third step delete from database tables """
    with sq.connect(config_data.config.data_base) as con:
        cur = con.cursor()
        for i in args:
            cur.execute('DROP TABLE IF EXISTS  {}'.format(i))


def clear_data(*args) -> None:
    """ Clear data from table """
    with sq.connect(config_data.config.data_base) as con:
        cur = con.cursor()
        for i in args:
            cur.execute('DELETE FROM {}'.format(i))


def select_all_data(data: str) -> list:
    """ Selection all data from table """
    with sq.connect(config_data.config.data_base) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM {}'.format(data))
        return cur.fetchall()


def write_data(string: str, values=tuple(), multistring=None) -> bool:
    """ Write data to our database """
    with sq.connect(config_data.config.data_base) as con:
        cur = con.cursor()
        try:
            if multistring is None:
                cur.executemany(string, values)
            elif len(values) != 0:
                cur.execute(string, values)
            else:
                cur.execute(string)
        except IOError as e:
            print(e)
            return False
        return True


def valid_data(string: str) -> Union[bool, str]:
    """ Data validation inside of database for table """
    try:
        with sq.connect(config_data.config.data_base) as con:
            cur = con.cursor()
            cur.execute(string)
            return cur.fetchone()[0]
    except IOError as e:
        print(e)
        return False


def write_history(table: tuple) -> bool:
    """ Data writing in the table history """
    return write_data(string=f"INSERT INTO history(uid, chat_id, datetime, city, check_in, check_out, quantity,"
                             f" quantity_photos, Error, commands, price_min, price_max, distance, period) "
                             f"VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", values=table)


def obtain_data_history(id: str) -> Union[bool, list]:
    """ Obtain filtered data from the table - history"""
    history_data = get_database(string='SELECT uid, datetime, commands, city, quantity, check_in, check_out,'
                                       ' price_min, price_max, distance, period, Error,'
                                       ' from history WHERE chat_id == {}'.format(id))
    for i in range(len(history_data)):
        if i != 0:
            return [i]
        else:
            return False


def obtain_data_hotels(uid: str) -> Union[bool, list]:
    """ Obtain chose data from the table - hotels """
    hotel_data = get_database(string='SELECT name, adress, hotel_id, coordinates, star_rating, user_rating, center,'
                                     ' price from hotels WHERE uid == { }'.format(uid))
    if len(hotel_data) != 0:
        return hotel_data
    else:
        return False


def write_hotels(hotels: tuple) -> bool:
    """ Data writing in the table hotels """
    return write_data(string=f"INSERT INTO hotels(uid, hotel_id, name, adress, center, price, coordinates, star_rating,"
                             f" user_rating) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", values=hotels, multistring=True)


def write_pictures(pictures: tuple) -> bool:
    """ Data writing in the table photos """
    return write_data(string=f"INSERT INTO photos(hotel_id, photo) VALUES(?, ?);", values=pictures, multistring=True)


def valid_pictures(hotel_id: str) -> int:
    """ Pictures validation in table - photos """
    return valid_data(string='SELECT Count(photo) FROM photos WHERE hotel_id == {}'.format(hotel_id))


def write_state(id: str, state: str) -> None:
    """ Write dataset inside the table - states """
    if valid_data(string='SELECT Count(chat_id) FROM states WHERE chat_id == {}'.format(id)):
        write_data('UPDATE states SET state == {} WHERE chat_id == {}'.format(state, id))
    else:
        write_data(string='INSERT INTO states(chat_id, state) VALUES(?, ?);', values=(id, state))


def write_check_date(id: int, check_out: str) -> None:
    """ Write dataset inside the table - inter_results """
    if valid_data(string='SELECT Count(user_id) FROM inter_results WHERE user_id == {}'.format(id)):
        write_data('UPDATE inter_results SET check_out_date == {} WHERE user_id == {}'.format(check_out, id))
    else:
        write_data(string='INSERT INTO inter_results(user_id, check_out_date) VALUES(?, ?);', values=(id, check_out))


def get_temporary_state(id: str) -> str:
    """ Obtain chose data from the table - states"""
    state = get_database(string='SELECT state from states WHERE chat_id == {}'.format(id))
    if len(state) != 0:
        return state[0][0]
    return '0'


def obtain_data_pictures(hotel_id: str, limit: str) -> list:
    """ Obtain chose data from the table - photos"""
    return get_database(string='SELECT photo from photos WHERE hotel_id == {} LIMIT {}'.format(hotel_id, limit))