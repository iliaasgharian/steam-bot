# 🎮 Steam Deals Telegram Bot

###### A Python Telegram bot that automatically tracks Steam game discounts, posts new discounts to the Telegram channel, and allows users to search for games or receive notifications when their desired game is discounted.

### ✨ Features
- 🔥 Automatically gets the latest Steam discounts

- 📢 Posts new deals to a Telegram channel

- 🔍 Allows users to search discounted games
- ❤️ Wishlist system:
  - Users can add a game to wishlist if it’s not on sale
   - The bot notifies and alerts the user when the game is discounted.
- 🕐 Deals update every 3 minutes
- 🕧 Full game database updates every 10 minutes
- 🧵 Multi-threaded 

### 🤖 Bot Commands
- `/start` :

  * Starts the bot

  * Shows welcome message

  * Provides channel link

- `/help` :

  * Shows how the user can work

- `/search GAME_NAME` :

  * Searches discounted games

  * If not found, adds the game to wishlist automatically

- `/end_notif` :

  * Removes all wishlist entries

  * Disables notifications

### 📦 Requirements 
####  These libraries must be installed.
```python
pip install requests
pip install python-telegram-bot
```
#### Python version:
```python
Python 3.8+
```
### ⚙️ Configuration
- Edit these variables at the top of the script:
```python
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_USERNAME = "@your_channel_username"
CHANNEL = "your_channel_username"
```
#### Make sure:
- The bot is admin in the channel
- The channel is public

## 🗄️ Database Structure
##### The database file will be created automatically.
##### SQLite database (`steam.db`) includes:
### users :

| column | Description |
|--------|------------|
| chat_id | Telegram user ID |

### wishlist :

| column | Description |
|--------|------------|
| chat_id | Telegram user ID |
| game_name | Desired game|

### deals:

| column | Description |
|--------|------------|
| title | Game title |
| normalPrice | Discounted price |
| salePrice | Price before discount |
| savings | Game discount amount |
| url | Game link on Steam |


### all_games:

| column | Description |
|--------|------------|
| title | Game title |
| normalPrice | Price before discount |
| salePrice | Discounted price |
| savings | Game discount amount |
| url | Game link on Steam |

##### ❗Note : Normal Price and Sale Price have been moved in all_games and deals.

## 🧠 How It Works

### The bot uses multiple background threads:

| Thread | Responsibility |
|--------|------------|
| telegram_worker | Handles `/start`, `/help`, `/search`, `/end_notif` |
| deals_worker | Fetches new Steam deals and posts them to the channel |
| get_all_games_periodic | Updates the local Steam games database |
| check_wish| Checks wishlists and notifies users when games go on sale |

##### ⚪ All data is stored locally using SQLite.

## 🚀 Startup Behavior

#### When it is runed:
##### 1. Fetches all Steam games
##### 2. Posts random deals to the channel
##### 3. Starts all background workers :
```python
get_all_games()
first_start()
```
## Game discount message structure in the channel
```python
f"🎮 {title}\n"
f"💰 Sale: {sale_price}$\n"
f"💵 Normal: {normal_price}$\n"
f"🔥 Discount: {discount}%\n"
f"🔗 {url2}"
```
- Example :
```python
🎮 Shadow of the Tomb Raider: Definitive Edition
💰 Sale: 4.0$
💵 Normal: 39.99$
🔥 Discount: 89.99%
🔗 https://store.steampowered.com/app/750920
```

## 🔔 Wishlist Notification Example
- If a user searches for a game that is not discounted:

```python
"❌ No result found"
"📢 We'll add this game to your wishlist and let you know as soon as the sale starts."
```
- When the game goes on sale:

```python
"💢 You searched for this game, and now it's on sale!"
```
### 🔶 Notes
- SQLite is shared across threads
- Heavy DB operations may cause slight delays
- Avoid very frequent message sending (Telegram rate limits)
