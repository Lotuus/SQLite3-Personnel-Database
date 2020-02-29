import sqlite3 as sq
import sys
import re

sys.setrecursionlimit(5000)  # set a higher recursion limit for error checking

""" create & use a db file if there is none; :memory: creates new file within memory for each run """
conn = sq.connect('personnel.db')

c = conn.cursor()  # cursor to operate through file

""" table with categorized info to be filled in; exists indefinitely once created """
# c.execute("""CREATE TABLE personnel (
#             last text,
#             first text,
#             grade integer,
#             stream text,
#             role text,
#             comments text
#             )""")


class Person:
    """ class for attributes of a person """
    def __init__(self, last, first, grade, stream, role, comments):
        self.ln = last
        self.fn = first
        self.gr = grade
        self.sr = stream
        self.rl = role
        self.cm = comments

    """ full name of a person """
    @property
    def fullname(self):
        return '{} {}'.format(self.fn, self.ln)


def s_sort(l):
    """ a selection sort algorithm; requires a list """
    for x in range(len(l)):  # while 1st index in range of length of list...
        min_i = x  # set 1st index as current min index, to be referenced/compared against

        for y in range(x + 1, len(l)):  # while 2nd index in range of 1st+1 & length of list...
            if l[min_i] > l[y]:  # if 1st is greater than 2nd, set 2nd as new min index
                min_i = y

        l[x], l[min_i] = l[min_i], l[x]  # swap new min with original reference


def check(ch, chs):
    """ recursion error check """
    if ch not in chs:
        print('Applicable responses: ', chs)
        ch = input('Please enter an applicable response.\n')
        return check(ch, chs)  # if not applicable, perform recursion
    return ch


def check_int(ch, chs):
    """ recursion error check for int input"""
    if ch not in chs:
        print('Applicable responses: ', chs)
        ch = int(input('Please enter an applicable response.\n'))
        return check(ch, chs)  # if not applicable, perform recursion
    return ch


def y_n(ch):
    """ function for determining yes-no chs """
    chs = ['yes', 'y', 'no', 'n']
    ch = check(ch, chs)

    if ch == 'yes' or ch == 'y':
        return True
    return False


def start():
    """ ask for user's desired action """
    acts = ['add', 'a', 'remove', 'r', 'search', 's', 'update', 'u', 'exit', 'e']  # list of allowed user defined inputs
    act = re.sub(r'\s', '', str(input('Would you like to ADD entry, REMOVE entry, SEARCH, UPDATE, or EXIT?\n'))
                 .lower())  # lower all letters, then remove whitespaces

    act = check(act, acts)  # perform error check

    """ take user to next stages according to their input """
    if act == 'add' or act == 'a':
        add()
    elif act == 'remove' or act == 'r':
        remove()
    elif act == 'search' or act == 's':
        search()
    elif act == 'update' or act == 'u':
        update()
    else:
        print('Exiting database...')
        conn.close()  # close operations
        sys.exit(0)


def add():
    """ function for inserting a person into tables with user inputs"""
    ch = input('You are about to ADD an entry. If NO, you may choose another option.\n').lower()

    if y_n(ch):
        print('Enter info for the following fields...\n')
        xln = re.sub(r'\s', '', str(input('Last name?\n')).lower().capitalize())  # lower, cap first, remove whitespace
        xfn = re.sub(r'\s', '', str(input('First name?\n')).lower().capitalize())

        if search2(xln, xfn):  # search if an entry already exists for user's input
            print('An entry already exists for', xfn, xln, end='. Please enter another entry.\n')
            return add()  # if an entry already exists make user enter another

        xgr = None
        try:  # try except user's inputted grade
            xgr = int(input('Grade?\n'))
            xgrs = [8, 9, 10, 11, 12, 13]

            xgr = check_int(xgr, xgrs)
        except ValueError:
            print('You did not enter an applicable grade. Please enter another value.')
            add()

        xsr = str(input('Stream? (eg. Academic, IB, etc...)\n')).lower().capitalize()
        xrl = str(input('Role? (eg. Design Member)\n')).lower().capitalize()
        xcm = str(input('Any comments?\n')).lower().capitalize()

        ch2 = input('Are you sure you wish to add this individual to the database? YES or NO?\n')
        if y_n(ch2):
            print(xfn, xln, 'has been added to the database.')
            with conn:  # input corresponding info to table with context manager
                c.execute("""INSERT INTO personnel VALUES (
                            :last, :first, :grade, :stream, :role, :comments)""",
                          {'last': xln, 'first': xfn, 'grade': xgr, 'stream': xsr, 'role': xrl, 'comments': xcm})

            start()  # after user's action has been completed, ask for another
        else:
            print('Your add action has been cancelled.')
            start()
    else:  # ask for another if user wishes to perform another action
        start()


def add2(p):
    """ function to add a person into table using class Person, without user inputs """
    with conn:  # context manager
        c.execute("""INSERT INTO personnel VALUES (
                    :last, :first, :grade, :stream, :role, :comments)""",
                  {'last': p.ln, 'first': p.fn, 'grade': p.gr, 'stream': p.sr, 'role': p.rl, 'comments': p.cm})


def remove():
    """ function for removing a person from the table, with user inputs"""
    ch = input('You are about to REMOVE an entry. If NO, you may choose another option.\n').lower()

    if y_n(ch):
        print('Enter info for the following fields...\n')
        xln = re.sub(r'\s', '', str(input('Last name?\n'))).lower().capitalize()
        xfn = re.sub(r'\s', '', str(input('First name?\n'))).lower().capitalize()

        if not search2(xln, xfn):
            print('No entry exists for', xfn, xln, end='. Please enter another entry.\n')
            return remove()

        ch2 = input('Are you sure you wish to remove this individual from the database? YES or NO?\n')
        if y_n(ch2):
            print(xfn, xln, 'has been removed from the database.')
            with conn:
                c.execute("""DELETE from personnel WHERE first=:first COLLATE NOCASE and last=:last COLLATE NOCASE""",
                          {'first': xfn, 'last': xln})

            start()
        else:
            print('Your remove action has been cancelled.')
            start()
    else:
        start()


def remove2(p):
    """ function for removing a person from the table with class Person, without user inputs """
    with conn:
        c.execute("""DELETE from personnel WHERE first=:first COLLATE NOCASE and last=:last COLLATE NOCASE""",
                  {'first': p.fn, 'last': p.ln})


def search():
    """ function for searching for a person within the table, with user inputs """
    ch = input('You are about to SEARCH for an entry. If NO, you may choose another option.\n').lower()

    if y_n(ch):
        print('Enter your desired subject to search in...\n')
        chs2 = ['last name', 'l', 'first name', 'f', 'grade', 'g', 'stream', 's', 'role', 'r']
        ch2 = input('Search by LAST NAME, FIRST NAME, GRADE, STREAM, or ROLE?\n').lower()
        ch2 = check(ch2, chs2)

        if ch2 == 'last name' or ch2 == 'l':
            query(ln_s(re.sub(r'\s', '', str(input('Desired last name?\n')))))
        elif ch2 == 'first name' or ch2 == 'f':
            query(fn_s(re.sub(r'\s', '', str(input('Desired first name?\n')))))
        elif ch2 == 'grade' or ch2 == 'g':
            try:
                xgr = int(input('Desired grade?\n'))
                xgrs = [8, 9, 10, 11, 12, 13]

                xgr = check_int(xgr, xgrs)
                query(gr_s(xgr))
            except ValueError:
                print('You did not enter an applicable grade. Please enter another value.')
                search()
        elif ch2 == 'stream' or ch2 == 's':
            query(sr_s(str(input('Desired stream?\n'))))
        else:
            query(rl_s(str(input('Desired role?\n'))))
    else:
        start()


def search2(ln, fn):
    """ function for searching for a person prior to modification """
    with conn:
        c.execute("""SELECT * FROM personnel WHERE first=:first COLLATE NOCASE AND last=:last COLLATE NOCASE""",
                  {'last': ln, 'first': fn})
        return c.fetchall()


# functions to search by an input, case insensitive
def query(q):
    """ handle search results """
    if q:  # if found, print sorted list
        for x in q:
            print(x)
    else:
        print('No results found.')

    start()


def ln_s(ln):
    """ search within table by last name """
    c.execute("SELECT * FROM personnel WHERE last=:last COLLATE NOCASE ", {'last': ln})
    return c.fetchall()  # returns a list of found items, empty if none found


def fn_s(fn):
    """ search within table by first name """
    c.execute("SELECT * FROM personnel WHERE first=:first COLLATE NOCASE", {'first': fn})
    return c.fetchall()


def gr_s(gr):
    """ search within table by grade """
    c.execute("SELECT * FROM personnel WHERE grade=:grade COLLATE NOCASE", {'grade': gr})
    return c.fetchall()


def sr_s(sr):
    """ search within table by stream """
    c.execute("SELECT * FROM personnel WHERE stream=:stream COLLATE NOCASE", {'stream': sr})
    return c.fetchall()


def rl_s(rl):
    """ search within table by role """
    c.execute("SELECT * FROM personnel WHERE role=:role COLLATE NOCASE", {'role': rl})
    return c.fetchall()


def update():
    """ function for updating info of a person within the table, with user inputs """
    ch = input('You are about to UPDATE an entry. If NO, you may choose another option.\n').lower()

    if y_n(ch):
        print('Enter info for the following fields...\n')
        xln = re.sub(r'\s', '', str(input('Last name?\n'))).lower().capitalize()
        xfn = re.sub(r'\s', '', str(input('First name?\n'))).lower().capitalize()

        if not search2(xln, xfn):
            print('No entry exists for', xfn, xln, end='. Please enter another entry.\n')
            return update()

        chs2 = ['grade', 'g', 'stream', 's', 'role', 'r', 'comment', 'c']
        ch2 = input('What information would you like to update? Previous data will be cleared.\n')
        ch2 = check(ch2, chs2)

        if ch2 == 'grade' or ch2 == 'g':
            try:
                xgr = int(input('New grade for {} {}?\n'.format(xfn, xln)))
                xgrs = [8, 9, 10, 11, 12, 13]

                xgr = check_int(xgr, xgrs)
                gr_u(xln, xfn, xgr)
            except ValueError:
                print('You did not enter an applicable grade. Please enter another value.')
                search()
        elif ch2 == 'stream' or ch2 == 's':
            xsr = input('New stream for {} {}?\n'.format(xfn, xln)).lower().capitalize()
            sr_u(xln, xfn, xsr)
        elif ch2 == 'role' or ch2 == 'r':
            xrl = input('New role for {} {}?\n'.format(xfn, xln)).lower().capitalize()
            rl_u(xln, xfn, xrl)
        else:
            xcm = input('New comment for {} {}?\n'.format(xfn, xln)).lower().capitalize()
            rl_u(xln, xfn, xcm)
    else:
        start()


# functions to update a piece of info for a person, case insensitive
def gr_u(ln, fn, gr):
    """ update grade of a person """
    with conn:
        c.execute("""UPDATE personnel SET grade=:grade
                    WHERE first=:first COLLATE NOCASE AND last=:last COLLATE NOCASE""",
                  {'first': fn, 'last': ln, 'grade': gr})

    print('New grade for ', fn, ln, end=': {}\n'.format(gr))
    start()


def sr_u(ln, fn, sr):
    """ update stream of a person """
    with conn:
        c.execute("""UPDATE personnel SET stream=:stream
                    WHERE first=:first COLLATE NOCASE AND last=:last COLLATE NOCASE""",
                  {'first': fn, 'last': ln, 'stream': sr})

    print('New stream for ', fn, ln, end=': {}\n'.format(sr))
    start()


def rl_u(ln, fn, rl):
    """ update role of a person """
    with conn:
        c.execute("""UPDATE personnel SET role=:role
                    WHERE first=:first COLLATE NOCASE AND last=:last COLLATE NOCASE""",
                  {'first': fn, 'last': ln, 'role': rl})

    print('New grade for ', fn, ln, end=': {}\n'.format(rl))
    start()


def cm_u(ln, fn, cm):
    """ update comments of a person """
    with conn:
        c.execute("""UPDATE personnel SET comments=:comments
                    WHERE first=:first COLLATE NOCASE AND last=:last COLLATE NOCASE""",
                  {'first': fn, 'last': ln, 'comments': cm})

    print('New grade for ', fn, ln, end=': {}\n'.format(cm))
    start()


if __name__ == "__main__":
    print('Welcome to the database.')
    start()

    conn.close()

sys.exit(0)
