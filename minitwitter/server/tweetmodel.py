from server.log import log
import sqlite3 as sqlite
import re


class TweetError(Exception):
    """Error handling user data."""

    def __init__(self, msg=''):
        self.msg = msg


class Tweets:
    """The tweet collection."""

    def __init__(self, db_connection=None):

        if not db_connection:
            self.con = sqlite.connect('tweet.db')
            self.con.row_factory = sqlite.Row
        else:
            self.con = db_connection  # assign an open db connection

        with self.con:  # CREATE TABLE is necessary and make sure default data is present
            cur = self.con.cursor()
            cur.executescript("""
              CREATE TABLE IF NOT EXISTS tweets(username TEXT, message TEXT, date TEXT);
              """)

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d


    def createTweet(self, username, message):
        """Create a new tweet in db. Returns 1 if inserted, 0 if not."""

        import datetime
        now = datetime.datetime.utcnow().strftime("%d.%m.%Y %H:%M:%S")

        with self.con:
            cur = self.con.cursor()
            query = "INSERT OR IGNORE INTO tweets VALUES(?, ?, ?)"
            cur.execute(query, (username, message, now))
            return cur.rowcount

    def deleteTweet(self, username, message):
        with self.con:
            cur = self.con.cursor()
            query = "DELETE FROM tweets WHERE username=? and message=?"
            cur.execute(query, (username, message))
            return cur.rowcount

    def findByUsername(self, username):
        with self.con:
            cur = self.con.cursor()
            query = "SELECT * FROM tweets WHERE username=?"
            cur.execute(query, (username,))
            row = cur.fetchone()
            log(2, "findByUsername(%s)=%s" % (username, row if row else "[empty result]"))

        if row:
            return Tweet(row)
        else:
            None  # None if no user found

    def findTweets(self):
        with self.con:
            cur = self.con.cursor()
            query = "SELECT * FROM tweets"
            cur.execute(query)
            rows = cur.fetchall()
        return [Tweet(row) for row in rows]



class Tweet:
    """A Tweet."""

    def __init__(self, row):
        """Constructs a user with username and arbitratry additional attributes."""
        self.username = row['username']
        for key in row.keys():  # set all other parameters as object attributes
            setattr(self, key, row[key])



if __name__ == '__main__':
    db = Tweets()
    db.createTweet("joarndt", "hey guys")
    db.createTweet("joarndt", "luuuuul")


    for x in db.findTweets():
        print(x.username, ": ", x.message, " ", x.date)





