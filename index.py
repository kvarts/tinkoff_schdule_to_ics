import configuration
import logging
import re
import datetime
import arrow
import time
from ics import Calendar, Event
from telegram.ext import Updater, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

month_map = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def parse_date(date_str):
    result = re.match("(\d+)\s+(\w+)\s+\(\w+\)", date_str).groups()

    day = int(result[0])
    month = month_map[result[1]]

    date = datetime.date(datetime.datetime.now().year, month, day)

    return date


def parse_start_end(interval_str):
    result = re.match("\w+\s+(\d+:\d+)\s+\w+\s+(\d+:\d+)", interval_str).groups()

    return [str(result[0]) + ":00", str(result[1]) + ":00"]


def try_convert_to_event(row):
    date_and_interval = row.split(" - ")
    date_str = date_and_interval[0]
    interval_str = date_and_interval[1]

    start_date = parse_date(date_str)
    end_date = start_date
    start_and_end_times = parse_start_end(interval_str)
    start_time = start_and_end_times[0]
    end_time = start_and_end_times[1]

    end_time_parts = end_time.split(":")
    if int(end_time_parts[0]) == 24:
        end_time = "00:" + str(end_time_parts[1]) + ":" + str(end_time_parts[2])
        end_date = end_date + datetime.timedelta(days=1)

    e = Event()
    e.name = "На работу!"
    e.begin = arrow.get(start_date.strftime("%Y%m%d ") + start_time, "%YYYY%MM%DD %HH:%mm:%ss").replace(tzinfo='Europe/Moscow')
    e.end = arrow.get(end_date.strftime("%Y%m%d ") + end_time, "%YYYY%MM%DD %HH:%mm:%ss").replace(tzinfo='Europe/Moscow')

    return e


def try_convert_schedule(update, context):
    text = update.message.text

    context.bot.send_message(chat_id=update.effective_message.chat_id, text='Пару секунд...')

    try:
        rows = text.split("\n")

        c = Calendar()
        for row in rows:
            try:
                e = try_convert_to_event(row)
                if e is not None:
                    c.events.add(e)
            except:
                print('error in Parse row = ' + row)

        content = str(c).replace("\r", "")
        filename = 'schedule_' + str(time.time()) + '.ics'
        with open(filename, 'w', encoding='utf-8') as my_file:
            my_file.write(content)

        context.bot.send_document(chat_id=update.effective_message.chat_id, document=open(filename, 'rb'))

    except:
        context.bot.send_message(chat_id=update.effective_message.chat_id, text="Ошибочка вышла 😔\nОбратитесь к https://t.me/ivan_kochergin")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(configuration.telegram["token"], use_context=True)

    updater.dispatcher.add_handler(MessageHandler(Filters.text, try_convert_schedule))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
