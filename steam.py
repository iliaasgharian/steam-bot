import requests
from datetime import datetime
import sqlite3
import time
import threading
import random


TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_USERNAME = "@your_channel_username"
CHANNEL = "your_channel_username"

url = "https://www.cheapshark.com/api/1.0/deals"
count = 50
params = {
    "sortBy": "Recent",
    "pageSize": count,
    "pageNumber": 0,
    "storeID": 1
}

db_file = "steam.db"


interval_seconds = 60


last_update_id = None


def send_to_telegram_channel(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_USERNAME,
        "text": text,
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, data=data, timeout=10)
        print("sent!!!!")
    except:
        print("networkError")


def send_private_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)


conn = sqlite3.connect(db_file, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    normalPrice REAL,
    salePrice REAL,
    savings REAL,
    url TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS times (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time INTEGER
)
""")
c.execute("""
          CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id string
)
          
          """)
c.execute("""
          CREATE TABLE IF NOT EXISTS wishlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id string,
    game_name string
)
          
          """)
conn.commit()


def set_user(chatid):
    c.execute("""
        INSERT INTO users (chat_id)
        VALUES ({})
          
          """.format(chatid))
    conn.commit()


def set_wishlist(chatid, title):
    c.execute("""
        INSERT INTO wishlist (chat_id,game_name)
        VALUES ('{}','{}')
          
          """.format(chatid, title))
    conn.commit()


def delete_notif(chat_id):
    c.execute("delete from wishlist where chat_id=='{}'".format(chat_id))
    conn.commit()
    msg = """🔇All games on your wishlist have been removed and notifications have been disabled.
🔴You can add a game to your wishlist by searching for it"""

    send_private_message(chat_id, msg)


def check_wish():
    while True:
        try:
            time.sleep(60)
            s = c.execute("select * from wishlist").fetchall()

            for i in s:
                name = i[2]
                cid = i[1]
                all = c.execute(
                    "select * from deals where title like '%{}%'".format(name)).fetchall()
                for n in all:
                    print(cid, n)

                    msg = (

                        "🔍 Search Result:\n"
                        f"🎮 {n[1]}\n"
                        f"💰 Sale: {n[2]}$\n"
                        f"💵 Normal: {n[3]}$\n"
                        f"🔥 Discount: {n[4]}%\n"
                        f"🔗 {n[5]}"
                        "💢You searched for this game, and now it's on sale."
                    )
                    send_private_message(cid, msg)

                    c.execute("delete from wishlist where id='{}'".format(i[0]))
                    conn.commit()
                    # print("sent a wishlist to a user!")
        except:
            print("Error while checking")


def first_start():

    num = random.randint(0, 50)
    params = {
        "sortBy": "Recent",
        "pageSize": count,
        "pageNumber": num,
        "storeID": 1
    }
    r = requests.get(url, params=params, timeout=30)
    data = r.json()
    for _ in range(10):
        i = random.randint(0, 45)
        title = data[i]["title"]
        normal_price = data[i]["normalPrice"]
        sale_price = data[i]["salePrice"]
        discount = data[i]["savings"]
        steam_id = data[i]["steamAppID"]
        url2 = f"https://store.steampowered.com/app/{steam_id}" if steam_id else "N/A"

        msg = (
            "🔍 Search Result:\n"
            f"🎮 {title}\n"
            f"💰 Sale: {sale_price}$\n"
            f"💵 Normal: {normal_price}$\n"
            f"🔥 Discount: {discount}%\n"
            f"🔗 {url2}"
        )
        print(msg)
        send_to_telegram_channel(msg)


def serach(chat_id, word):
    rows = c.execute("""
        SELECT *
        FROM all_games
        WHERE title LIKE ?
    """, (f"%{word}%",)).fetchall()
    if not rows:
        send_private_message(chat_id, """❌ No result found
📢 We'll add this game to your wishlist and let you know as soon as the sale starts.
                             """)
        set_wishlist(chat_id, word)
        return

    for i in rows:
        title = i[1]
        normal_price = i[2]
        sale_price = i[3]
        discount = i[4]
        url2 = i[5]

        msg = (
            "🔍 Search Result:\n"
            f"🎮 {title}\n"
            f"💰 Sale: {sale_price}$\n"
            f"💵 Normal: {normal_price}$\n"
            f"🔥 Discount: {discount}%\n"
            f"🔗 {url2}"
        )

        print(msg)
        send_private_message(chat_id, msg)


def check_start_command():
    global last_update_id

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 1}

    if last_update_id:
        params["offset"] = last_update_id + 1

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if not data.get("ok"):
            return

        for update in data["result"]:
            last_update_id = update["update_id"]

            if "message" not in update:
                continue

            msg = update["message"]
            text = msg.get("text", "")
            chat_id = msg["chat"]["id"]

            if text == "/start":
                welcome_text = (
                    "👋 Hello!\n\n"
                    "🎮 This bot automatically finds Steam discounts\n"
                    "📢 Deals are published in the channel\n\n"
                    "🔍 Use:\n"
                    "/help\n\n"
                    "To understand how to use the robot\n"
                    f"Join our <a href='https://t.me/{CHANNEL}'>channel</a> to see the lastest discounts"
                )
                s = c.execute(
                    "select * from users where chat_id='{}'".format(chat_id)).fetchall()
                if len(s) == 0:
                    set_user(chat_id)
                send_private_message(chat_id, welcome_text)

            if text.startswith("/search "):
                word = text.split(" ", 1)[1].strip()
                print("SEARCH:", word)
                serach(chat_id, word)
            if text == "/help":
                help_text = (
                    "🤖 Steam Deals Bot – Help\n\n"
                    "🎮 What this bot does:\n"
                    "• Finds Steam game discounts automatically\n"
                    "• Publishes new deals in the channel\n"
                    "• Lets you search discounted games\n\n"
                    "📌 Commands:\n"
                    "▶ /start\n"
                    "  Start the bot and get info\n\n"
                    "▶ /search GAME_NAME\n"
                    "  Search for a discounted Steam game\n"
                    "  Example:\n"
                    "  /search red dead\n\n"
                    "▶ /end_notif:\n"
                    """All games on your wishlist will be removed and notifications will be disabled.
                    You can add the game to your wishlist by searching for it. Re-enable notifications\n"""
                    "🔔 Automatic:\n"
                    "• New Steam discounts are posted every minute\n"
                    "• Game database updates every 10 minutes\n\n"
                    f"💢 Join our <a href='https://t.me/{CHANNEL}'>channel</a> to see the lastest discounts\n"

                )
                send_private_message(chat_id, help_text)
            if text == "/end_notif":
                delete_notif(chat_id)
    except Exception as e:
        print("Update Error:", e)


def telegram_worker():
    while True:
        check_start_command()
        time.sleep(0.3)


def get_all_games():
    c.execute("DROP TABLE IF EXISTS all_games;")
    c.execute("""
    CREATE TABLE IF NOT EXISTS all_games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        normalPrice REAL,
        salePrice REAL,
        savings REAL,
        url TEXT
    )
    """)
    i = 0
    while True:
        url = "https://steamspy.com/api.php?request=all&page={}".format(i)
        while True:
            try:
                response = requests.get(url, timeout=10)
                break
            except requests.exceptions.RequestException as e:

                time.sleep(1)

        if len(response.text) < 100:
            break
        else:
            data = response.json()

            for d in data:
                discount = data[d]["discount"]
                appid = data[d]["appid"]
                title = data[d]["name"]
                try:
                    normalprice = int(data[d]["initialprice"])/100
                    saleprice = int(data[d]["price"])/100
                    link = "https://store.steampowered.com/app/{}".format(
                        appid)
                    if int(discount) != 0:
                        c.execute("""
                            INSERT INTO all_games (title, normalPrice, salePrice, savings, url)
                            VALUES (?, ?, ?, ?, ?)
                        """, (title, normalprice, saleprice, discount, link))

                except:
                    print(i, appid)
            conn.commit()

            print(i, "completed")

            i += 1

    vb = c.execute("select * from deals")

    for i in vb:
        name = i[1]
        normalprice = i[2]
        saleprice = i[3]
        savings = i[4]
        link = i[5]
        s = c.execute(
            "select * from all_games where title=?",
            (name,)
        ).fetchall()
        try:
            print(list(s)[1])
        except:
            c.execute("""
                            INSERT INTO all_games (title, normalPrice, salePrice, savings, url)
                            VALUES (?, ?, ?, ?, ?)
                        """, (name, normalprice, saleprice, savings, link))
    conn.commit()

    vb = c.execute("select * from deals")
    for i in vb:
        tit = list(i)[1]
        normalprice = list(i)[2]
        saleprice = list(i)[3]
        savings = list(i)[4]
        link = list(i)[5]
        if len(list(c.execute("select * from all_games where title='{}'".format(tit)))) == 0:
            c.execute("""
                            INSERT INTO all_games (title, normalPrice, salePrice, savings, url)
                            VALUES (?, ?, ?, ?, ?)
                        """, (tit, normalprice, saleprice, savings, link))
    conn.commit()
    c.execute("""
    DELETE FROM all_games
    WHERE rowid NOT IN (
    SELECT MAX(rowid)
    FROM all_games
    GROUP BY title
);                      
              """)
    conn.commit()


def get_all_games_periodic():
    while True:
        time.sleep(600)
        print("start updating...")
        try:
            get_all_games()
        except Exception as e:
            print("error in all games:", e)
        print("all games has been get ✅")


def deals_worker():
    li = []
    new_times = []

    while True:
        try:
            print("started :")

            times = list(c.execute("SELECT time FROM times"))
            if not times:
                first_time = int(deals[0]["lastChange"])
                c.execute("INSERT INTO times (time) VALUES (?)", (first_time,))
                conn.commit()

            last_saved_time = list(c.execute("SELECT time FROM times"))[-1][0]
            # print(last_saved_time)
            print("Last saved time:", datetime.fromtimestamp(last_saved_time))

            new_times = []
            m = 0

            while m < 1:
                params = {
                    "sortBy": "Recent",
                    "pageSize": count,
                    "pageNumber": m,
                    "storeID": 1
                }
                response = requests.get(url, params=params, timeout=(10, 45))
                deals = response.json()
                for deal in deals:
                    title = deal["title"]
                    sale_price = deal.get("salePrice", "N/A")
                    normal_price = deal.get("normalPrice", "N/A")
                    discount = deal.get("savings", "0")[:5]

                    steam_id = deal.get("steamAppID")
                    url2 = f"https://store.steampowered.com/app/{steam_id}" if steam_id else "N/A"

                    last_change_ts = int(deal["lastChange"])

                    if last_change_ts > last_saved_time:
                        msg = (
                            f"🎮 {title}\n"
                            f"💰 Sale: {sale_price}$\n"
                            f"💵 Normal: {normal_price}$\n"
                            f"🔥 Discount: {discount}%\n"
                            f"🔗 {url2}"
                        )

                        li.append(msg)

                        c.execute("""
                            INSERT INTO deals (title, normalPrice, salePrice, savings, url)
                            VALUES (?, ?, ?, ?, ?)
                            """, (title, normal_price, sale_price, discount, url2))

                        new_times.append(last_change_ts)
                        conn.commit()

                m += 1

        except Exception as e:
            print("Connection Error:", e)
        try:
            print(sorted(new_times)[-1])
            c.execute("INSERT INTO times (time) VALUES (?)",
                      (sorted(new_times)[-1],))
            conn.commit()
            c.execute("""
                DELETE FROM deals
                WHERE rowid NOT IN (
                    SELECT MAX(rowid)
                    FROM deals
                    GROUP BY title
                );      
                            """)
            conn.commit()
            for ms in li:
                print(ms)
                send_to_telegram_channel(ms)
                time.sleep(1)
        except:
            print("newtimes is empty")
        print("end, next time 180 seconds later ...")
        time.sleep(180)


get_all_games()
first_start()

if __name__ == "__main__":
    t2 = threading.Thread(target=telegram_worker, daemon=True)
    t1 = threading.Thread(target=deals_worker, daemon=True)
    t3 = threading.Thread(target=get_all_games_periodic, daemon=True)
    t4 = threading.Thread(target=check_wish, daemon=True)
    t2.start()
    t4.start()
    t1.start()
    t3.start()
    while True:
        time.sleep(10)
