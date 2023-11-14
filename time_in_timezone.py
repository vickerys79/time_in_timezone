import datetime
import difflib
import pytz
import sqlite3


def connect_to_db(db_name):
    """
    Connects to the SQLite database and returns the connection and cursor.

    Args:
        db_name (str): The name of the SQLite database.

    Returns:
        tuple: A tuple containing the SQLite connection and cursor.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    return conn, cursor


def get_current_time_for_timezone(timezone_name):
    """
    Retrieves the current time for a given timezone.

    Args:
        timezone_name (str): The name of the timezone.

    Returns:
        str: A string representing the current time in the given timezone.
    """
    try:
        conn, cursor = connect_to_db(db_name='example_db')
        cursor.execute("SELECT time_now FROM timezone_times WHERE timezone=?", (timezone_name,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return f"Current time in {timezone_name}: {result[0]}"
        else:
            return (f"Timezone '{timezone_name}' not found and we cannot suggest any similar alternatives. "
                    f"Please check the spelling or try a different timezone.")

    except Exception as e:
        return f"An error occurred: {str(e)}"


def find_similar_timezones(user_timezone):
    """
    Finds similar timezones to the user-provided timezone.

    Args:
        user_timezone (str): The user-provided timezone.

    Returns:
        list: A list of similar timezones.
    """
    all_timezones_lower = [tz.lower() for tz in pytz.all_timezones]
    user_timezone_lower = user_timezone.lower()

    matches = difflib.get_close_matches(user_timezone_lower, all_timezones_lower, n=3, cutoff=0.6)

    return [pytz.all_timezones[all_timezones_lower.index(match)] for match in matches]


def main():
    """
    Main function to interact with the user and display timezone information.
    """
    user_timezone = input("Enter a timezone name: ").strip()
    if user_timezone not in pytz.all_timezones:
        similar_timezones = find_similar_timezones(user_timezone)

        if similar_timezones:
            print("Did you mean one of these?")
            for tz in similar_timezones:
                print("-", tz)
            main()
        else:
            print(f"Timezone '{user_timezone}' not found and we cannot suggest any similar alternatives. "
                  f"Please check the spelling or try a different timezone.")
    else:
        print(get_current_time_for_timezone(user_timezone))


if __name__ == "__main__":
    # retrieve timezone data
    timezone_data = []
    all_timezones = pytz.all_timezones
    for timezone_name in all_timezones:
        timezone = pytz.timezone(timezone_name)
        current_time = datetime.datetime.utcnow()
        current_time = pytz.utc.localize(current_time).astimezone(timezone)
        timezone_data.append((str(timezone), current_time.strftime('%Y-%m-%d %H:%M:%S')))

    # create DB table to contain timezone data. It is accepted that a DB may not be the best option for storing this
    # data, but I want to show that I can use this technology
    conn, cursor = connect_to_db(db_name='example_db')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timezone_times (
            id INTEGER PRIMARY KEY,
            timezone TEXT NOT NULL,
            time_now TEXT NOT NULL
        )
    ''')

    cursor.execute("DELETE FROM timezone_times")
    cursor.executemany("INSERT INTO timezone_times (timezone, time_now) VALUES (?, ?)",
                       timezone_data)

    conn.commit()
    conn.close()
    main()
