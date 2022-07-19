import datetime
from peewee import *
from telebot.types import Message

db = SqliteDatabase('history_dataset.db')


class HistoryOutput(Model):
    """
    Table creation contained parameters in database
    """
    id = PrimaryKeyField(unique=True)
    user_id = IntegerField(default=None)
    command = CharField(default=None)
    date = DateTimeField(default=datetime.datetime.now)
    hotel_list = TextField(default=None)

    class Meta:
        database = db
        table_name = 'History_data'
        order_by = 'id'


def history_writing(message: Message, hotel_list: str, command: str) -> None:
    """
    Function for recordings data related to command and date command inside of database
    :param message:
    :param hotel_list:
    :param command
    :return:
    """
    with db:
        HistoryOutput(user_id=message.chat.id, command=command,
                      date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), hotel_list=hotel_list).save()


def hist_get_out(user_id: int) -> list[str]:
    """
    Function for getting out all data about previous commands
    :param user_id: identificator of the user
    :return: list of strings
    """
    with db:
        history = HistoryOutput.select().where(HistoryOutput.user_id == user_id) \
            .order_by(HistoryOutput.date.desc()).limit(10).dicts().execute()
        if not history:
            return ['No command data presents yet, so the history is empty!\nPlease press the /start']
        command_list = [f'Command: {i_command.get("command")}\nDate of command: {i_command.get("date")}\n'
                        f'Hotels found:\n{i_command.get("hotel_list")}' for i_command in history]
    return command_list
