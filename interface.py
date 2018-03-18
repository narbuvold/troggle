import db
user=""

def main():
    global user
    while True:
        login = input("Input username:\n")
        if db.check_user(login):
            print("Welcome " + login)
            break
        else:
            verification = input("User does not exist, Do you want to create a new user [Y/n]\n")
            if not verification or verification == "y":
                db.add_user(login)
                print("Welcome " + login)
                break

    user = login
    while True:
        command = input(">>> ")
        if command:
            seq = command.split()
            if seq[0] == "quit":
                break
            parse_command(seq)
        else:
            print("Usage: get [...] | create <session type> | start <session type> | end <session type> | restart")


def parse_command(seq):
    if seq[0] == "get":
        GET(seq[1:])
    if seq[0] == "create":
        if seq[1:]:
            db.add_session_name(user, ' '.join(seq[1:]))
        else:
            print("usage: create <session type>")
    if seq[0] == "start":
        if seq[1:]:
            db.start_session(user, ' '.join(seq[1:]))
        else:
            print("usage: start <session type>")
    if seq[0] == "end":
        if seq[1:]:
            db.end_session(user, ' '.join(seq[1:]))
        else:
            print("usage: end <session type>")
    if seq[0] == "reset":
        db.drop_tables()
        db.setup_database()
        db.add_user(user)


def GET(seq):
    if not seq:
        print("Usage: get [active | finished | sessions | users | types | time [...]]")
    elif seq[0] == "active":
        print(db.get_active_sessions(user))
    elif seq[0] == "finished" or seq[0] == "sessions":
        print(db.get_finished_sessions(user))
    elif seq[0] == "users":
        print(db.get_all_users())
    elif seq[0] == "types":
        print(db.get_session_name(user))
    elif seq[0] == "time":
        TIME(seq[1:])


def TIME(seq):
    if not seq:
        print("Usage: get time [all | <session type>]")
    elif seq[0] == "all":
        print(db.get_all_times(user))
    else:
        print(db.get_total_time(user, ' '.join(seq)))
            

if __name__=="__main__":
    main()
