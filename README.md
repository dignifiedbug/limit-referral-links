# limit-referral-links
Enforce a cool-off period for links posted in your subreddit.

### Setup
Python 3.6

pip install [PRAW](https://github.com/praw-dev/praw)

### Configure
Add your account settings to praw.ini

*BOT_REPLY_TEXT* in referral_link_bot.py is your bot's response to comments, and *TIME_LIMIT* in db_handler.py is the cool-off period length for links.

### Run
Start referral_link_bot.py
