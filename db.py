from time import time, sleep, ctime
import sqlite3
conn = sqlite3.connect('case.db')
c = conn.cursor()

def setup_database():
    c.execute(
            """
            CREATE TABLE IF NOT EXISTS Users (
            Username varchar(20) UNIQUE
            );""")
    c.execute(
            """
            CREATE TABLE IF NOT EXISTS SessionName (
            Sessionname VARCHAR(20),
            Username VARCHAR(20),
            Active INTEGER,
            FOREIGN KEY (Username) REFERENCES users(Username),
            PRIMARY KEY (Sessionname, Username),
            FOREIGN KEY (Active) REFERENCES Sessions(SessionID)
            );""")
    c.execute(
            """
            CREATE TABLE IF NOT EXISTS Sessions (
            SessionID INTEGER PRIMARY KEY,
            Username VARCHAR(20),
            Sessionname VARCHAR(20),
            Start timestamp NOT NULL,
            Duration INTEGER,
            FOREIGN KEY (Username) REFERENCES Users(Username)
            FOREIGN KEY (Sessionname, Username) REFERENCES SessionName(Sessionname, Username)
            );""")

    conn.commit()


def drop_tables():
    c.execute('DROP TABLE IF EXISTS Users;')
    c.execute('DROP TABLE IF EXISTS Sessions;')
    c.execute('DROP TABLE IF EXISTS SessionName;')
    conn.commit()


def add_user(name):
    try:
        c.execute('INSERT INTO Users (Username) VALUES (?);', (name,))
        conn.commit()
    except sqlite3.DatabaseError as err:
        print(err)


def add_session_name(user, name):
    try:
        c.execute(
                """INSERT INTO SessionName (Sessionname, Username, Active)
                VALUES (?, ?, NULL)
                ;""",
                (name, user))
        conn.commit()
        return name + " created"
    except sqlite3.DatabaseError as err:
        print(err)
    

def start_session(user, session_name):
    try:
        c.execute('SELECT Active FROM SessionName WHERE Username=? AND Sessionname=?', (user, session_name))
        session_id = c.fetchone()
        if (session_id is None):
            print("Incorrect user or session")
            return
        if (session_id[0]):
            print("Session is already active")
            return
        c.execute(
                """
                INSERT INTO Sessions (Username, Sessionname, Start)
                VALUES (?, ?, ?);
                """,
                (user, session_name, time()))
        session_id = c.lastrowid
        c.execute(
                """
                UPDATE SessionName
                SET Active=?
                WHERE Username=? AND Sessionname=?;
                """,
                (session_id, user, session_name))
        conn.commit()
        return "Session " + session_name + " created"
    except sqlite3.DatabaseError as err:
        print(err)


def end_session(user, session_name):
    try:
        c.execute('SELECT Active FROM SessionName WHERE Username=? AND Sessionname=?', (user, session_name))
        session_id = c.fetchone()
        if (session_id is None):
            print("Incorrect user or session")
            return
        if (not session_id[0]):
            print("Session is not active")
            return
        session_id = session_id[0]
        c.execute('SELECT Start FROM Sessions WHERE SessionID = ?;', (session_id,))
        start_time = c.fetchone()[0]
        duration = round(time() - start_time)
        c.execute(
                """
                UPDATE Sessions
                SET Duration=?
                WHERE SessionID=?;
                """,
                (duration, session_id))
        c.execute(
                """
                UPDATE SessionName
                SET Active=null
                WHERE Username=? AND Sessionname=?;
                """, 
                (user, session_name))
        conn.commit()
        print("Session " + session_name + " ended after " + str(duration) + " seconds")
    except sqlite3.DatabaseError as err:
        print(err)


def get_all_times(user):
    try:
        c.execute(
                """
                SELECT Sessionname
                FROM SessionName
                WHERE Username=?
                ;""",
                (user,))
        session_names = c.fetchall()
        if session_names is None:
            print("User has no sessions")
            return
        res = []
        for session in session_names:
            duration = get_total_time(user, session[0])
            res += (session[0], duration)
        return res

    except sqlite3.DatabaseError as err:
        print(err)


def get_total_time(user, session_name):
    try:
        c.execute(
                """
                SELECT SUM(Duration) 
                FROM Sessions 
                WHERE Username=? AND Sessionname=?
                ;""",
                (user, session_name))
        duration = c.fetchone()
        if (duration[0] is None):
            return "No finished sessions"
        return duration[0]

    except sqlite3.DatabaseError as err:
        print(err)


def get_active_sessions(user):
    try:
        c.execute(
                """
                SELECT Start, Sessionname
                FROM Sessions
                WHERE SessionID IN (
                    SELECT Active
                    FROM SessionName
                    WHERE Username=?
                );
                """,
                (user,))
        res = c.fetchall()
        for i in range(len(res)):
            res[i] = (ctime(res[i][0]), res[i][1])
        return(res)

    except sqlite3.DatabaseError as err:
        print(err)


def get_finished_sessions(user, session_name="all"):
    try:
        if session_name == "all":
            c.execute(
                    """
                    SELECT Start, Duration, Sessionname
                    FROM Sessions
                    WHERE Username=?
                    ;""",
                    (user,))
        else:
            c.execute(
                    """
                    SELECT Start, Duration
                    FROM Sessions
                    WHERE Username=? AND Sessionname=?
                    ;""",
                    (user, session_name))
        result = c.fetchall()
        if result is None:
            print("No such sessions")
            return
        for i in range(len(result)):
            result[i] = (ctime(result[i][0]), result[i][1], result[i][2])
        return result

    except sqlite3.DatabaseError as err:
        print(err)



def get_all_users():
    c.execute('SELECT Username FROM Users;')
    users = []
    for user in c.fetchall():
        users += user
    return users


def get_session_name(user="all"):
    try:
        if user == "all":
            c.execute('SELECT Username, Sessionname FROM SessionName')
        else:
            c.execute('SELECT Sessionname FROM SessionName WHERE Username=?', (user,))
        return c.fetchall()
    except sqlite3.DatabaseError as err:
        print(err)


def check_user(user):
    try:
        c.execute('SELECT * FROM Users WHERE Username=?;', (user,))
        result = c.fetchall()
        return result != []
    except sqlite3.DatabaseError as err:
        print(err)
        return FALSE


def access_db(command):
    c.execute(command)
    conn.commit()


def fill_tables():
    add_user("Lome")
    add_session_name("Lome", "Work")
    add_session_name("Lome", "Play")
    add_user("Yamoussoukro")
    add_session_name("Yamoussoukro", "Work")
    add_session_name("Yamoussoukro", "Play")
    add_user("Antananarivo")
    add_session_name("Antananarivo", "Work")
    add_session_name("Antananarivo", "Play")
    add_user("Ouagadougou")
    add_session_name("Ouagadougou", "Work")
    add_session_name("Ouagadougou", "Play")
    add_user("Addis Abeba")
    add_session_name("Addis Abeba", "Work")
    add_session_name("Addis Abeba", "Play")


def run_tests():
    assert(get_all_users()== ['Lome', 'Yamoussoukro', 'Antananarivo', 'Ouagadougou', 'Addis Abeba'])
    assert(get_session_name("Addis Abeba") == [('Play',), ('Work',)])
    #print(get_session_name("all"))
    start_session("Lome", "Play")
    start_session("Lome", "Play")
    start_session("Lome", "Work")
    start_session("Hello", "World")
    c.execute('SELECT Username, Sessionname FROM SessionName Where Active=1;')
    assert(c.fetchall() == [('Lome', 'Play')])
    sleep(2)
    end_session("Lome", "Play")
    c.execute('SELECT * FROM SessionName WHERE Username="Lome"')
    start_session("Lome", "Play")
    sleep(2)
    end_session("Lome", "Play")
    end_session("Lome", "Work")
    print(get_finished_sessions("Lome", "all"))
    print(get_all_times("Lome"))
    
if __name__=="__main__":
    drop_tables()
    setup_database()
    fill_tables()
    run_tests()
    conn.close
