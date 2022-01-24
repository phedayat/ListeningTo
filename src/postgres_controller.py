import psycopg2 as post
import json
import os

class PostgresController:
    def __init__(self) -> None:
        # self.DATABASE_URL = "postgres://isbyzwksoaqibt:d268f7f77f51d7a4e846ac819d2c7397de5b035b3a5a49288b26aa6ba47cc3b2@ec2-54-160-96-70.compute-1.amazonaws.com:5432/dcs5eanfbcbq39"
        self.conn = post.connect(os.environ.get("DATABASE_URL"), sslmode="require")
        # self.conn = post.connect(self.DATABASE_URL, sslmode="require")
        self.cursor = self.conn.cursor()

    def insertUser(self, username, password):
        query = """
            INSERT INTO users (username, password, connection, songs, lastSong) VALUES (
                %s,
                crypt(%s, gen_salt('bf')),
                %s,
                %s,
                %s
            );
        """
        self.cursor.execute(query, vars=(username, password, None, [], None))
        self.conn.commit()
        return 1

    def getUser(self, username):
        query = """
            SELECT id, username, password, connection, lastSong, songs FROM users
            WHERE username = %s;
        """
        self.cursor.execute(query, vars=(username,))
        return (self.cursor.fetchone())[0]

    def getPassword(self, username):
        query = """
            SELECT password FROM users
            WHERE username = %s;
        """
        self.cursor.execute(query, vars=(username,))
        return (self.cursor.fetchone())[0]

    def getConnection(self, username):
        query = """
            SELECT connection FROM users
            WHERE username = %s;
        """
        self.cursor.execute(query, vars=(username,))
        res = self.cursor.fetchone()
        return res[0] if res else 0

    def getLastSong(self, username):
        query = """
            SELECT lastSong FROM users
            WHERE username = %s;
        """
        self.cursor.execute(query, vars=(username,))
        return (self.cursor.fetchone())[0]

    def getSongs(self, username):
        query = """
            SELECT songs FROM users
            WHERE username = %s;
        """
        self.cursor.execute(query, vars=(username,))
        return (self.cursor.fetchone())[0]

    def checkUserExists(self, username):
        query = """
            SELECT id FROM users
            WHERE username = %s;
        """
        self.cursor.execute(query, vars=(username,))
        return True if self.cursor.fetchone() else False

    def checkPassword(self, username, password):
        query = """
            SELECT id FROM users
            WHERE username = %s AND
                password = crypt(%s, password);
        """
        self.cursor.execute(query, vars=(username, password))
        return True if self.cursor.fetchone() else False

    def updateConnection(self, sender, target):
        if target == "*":
            query = """
                UPDATE users SET connection = NULL WHERE username = %s;
            """
            self.cursor.execute(query, vars=(sender,))
            self.conn.commit()
            return 2
        else:
            if self.checkUserExists(target):
                query = """
                    UPDATE users SET connection = %s WHERE username = %s;
                    UPDATE users SET connection = %s WHERE username = %s;
                """
                self.cursor.execute(query, vars=(target, sender, sender, target))
                self.conn.commit()
                return 1
            return 0


    def updatePassword(self, username, curr_pass, new_pass):
        if self.checkPassword(username, curr_pass):
            query = """
                UPDATE users SET password = crypt(%s, gen_salt('bf')) WHERE username = %s;
            """
            self.cursor.execute(query, vars=(new_pass, username))
            self.conn.commit()
            return 1
        return 0

    def updateSongs(self, username, song):
        query = """
            UPDATE users SET songs = array_append(songs, %s) WHERE username = %s;
        """
        self.cursor.execute(query, vars=(song, username))
        self.conn.commit()
        return 1

    def updateLastSong(self, username, song):
        query = """
            UPDATE users SET lastSong = %s WHERE username = %s;
        """
        self.cursor.execute(query, vars=(song, username))
        self.conn.commit()
        return 1

    def removeUser(self, username, password):
        if self.checkPassword(password):
            query = """
                DELETE FROM users WHERE username = %s;
            """
            self.cursor.execute(query, vars=(username,))
            self.conn.commit()
            return 1
        return 0

    def shutdown(self):
        self.cursor.close()
        self.conn.close()
        return 1

if __name__=="__main__":
    p = PostgresController()
    # print(p.insertUser("parsia", "12345"))
    # print(p.insertUser("jack", "67890"))
    print(p.getConnection("parsia"))
    # print(p.getUser("parsia"))
    # print(p.getUser("parsia"))
    # print(p.getUser("jack"))
    # print(p.checkPassword("parsia", "67890"))
    # print(p.updatePassword("parsia", "12345", "67890"))
    # print(p.updateConnection("parsia", "jack"))
    # print(p.getConnection("parsia")[0])
    # print(json.loads(p.getLastSong("jack"))["artist"])
    p.shutdown()
