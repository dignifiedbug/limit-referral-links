from urllib.parse import urlparse
import time
import re

import praw
import db_handler


# The message your bot will leave on removed comments.
BOT_REPLY_TEXT = ('Your comment was removed because it contained a link that has been posted before **in the last 30 days**.\n\n'
				  'If you believe this was an accident, message the moderators [here](https://www.reddit.com/message/compose?to=/r/creditcardreferrals).\n\n'
				  '---\n\n'
				  '^(This action was performed automatically by a bot.)')

# Links starting with a phrase in this list are always allowed to be posted.
WHITELIST = ('reddit.com', 'redd.it', 'np.reddit.com',
			 'np-dk.reddit.com', 'i.redd.it', 'imgur')

def main():
	site_name = 'Referral Link Bot'
	config = praw.config.Config(site_name)
	reddit = praw.Reddit(
		site_name,
		user_agent = '{}:v1 by /u/dignifiedbug'.format(config.client_id))
	subreddit = reddit.subreddit(config.custom['subreddit'])
	try:
		print('Referral Link Bot running...\nExit with Ctrl+C\n')
		loop(subreddit)
	except KeyboardInterrupt:
		print('\n[Interrupted]')
	finally:
		print('Process stopped.')
		time.sleep(3)

# Handle comments found with a duplicate link.
def handle_duplicates(users_comment):
	print('Comment with duplicate link(s): ' + users_comment.id)
	bot_response = users_comment.reply(BOT_REPLY_TEXT)
	bot_response.mod.distinguish()
	bot_response.save()
	users_comment.mod.remove()
	
def process_submission(comment):
	if not comment.saved:
		database = db_handler.DatabaseHandler('link_database.db')
		duplicate_links = []
		original_links = []
		comment.save()
		# Sort duplicate and original links.
		for link in find_links(comment.body):
			if link not in database.logged_links():
				original_links.append(link)
			else:
				duplicate_links.append(link)
		# Save links or escalate comment.
		if duplicate_links:
			handle_duplicates(comment)
		elif original_links:
			database.save_data(original_links, comment)
	
def find_links(text):
	# Find and format all URLs in text.
	regex = '(?=(?<=\A)|(?<=\W))(?:(?:(?:https?://)(?:www\.)?)|(?:www\.))([-A-z0-9+&@#/%=~_|$?!:,.]*[A-z0-9+&@#/%=~_|$])'
	simple_links = []
	for match in re.findall(regex, text, flags=re.IGNORECASE):
		urlp = urlparse(match.lower())
		parsed_together = urlp[2] + urlp[3] + urlp[4]
		if not parsed_together.startswith(WHITELIST):
			simple_links.append(parsed_together)
	return simple_links

def loop(subreddit):
	while True:
		try:
			for comment in subreddit.stream.comments():
				process_submission(comment)
		except Exception as e:
			print(e.args)
			print('Restarting in 30 minutes...')
			time.sleep(1800)

if __name__ == '__main__':
	main()
