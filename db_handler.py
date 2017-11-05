from datetime import datetime, timedelta
import sqlite3


# The time required to wait before reposting a referral link.
TIME_LIMIT = timedelta(days=30)

class DatabaseHandler:
	def __init__(self, db_name):
		self._connection = sqlite3.connect(db_name)
		self._connection.row_factory = lambda cursor, row: row[0]
		self._cursor = self._connection.cursor()
		self._create_table_if_not_exists()
		self._clean_old_links()
		
	def logged_links(self):
		self._cursor.execute("SELECT link from referral_list")
		return self._cursor.fetchall()
	
	def save_data(self, links, comment):
		for link in links:
			self._cursor.execute("INSERT INTO referral_list VALUES (?,?,?)",
				(link, comment.created_utc, comment.id))
			self._connection.commit()
	
	def _create_table_if_not_exists(self):
		self._cursor.execute(
			"CREATE TABLE IF NOT EXISTS referral_list \
			(link TEXT, time_created INTEGER, comment_id TEXT)")
		self._connection.commit()
	
	def _clean_old_links(self):
		unix_epoch = datetime(1970, 1, 1)
		cutoff_time = (datetime.utcnow() - TIME_LIMIT - unix_epoch).total_seconds()
		self._cursor.execute("DELETE FROM referral_list WHERE time_created <= ?", (cutoff_time,))
		self._connection.commit()
	
	def __del__(self):
		self._connection.close()
