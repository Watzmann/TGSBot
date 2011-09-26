#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Administrative commands."""

REV = '$Revision$'

import inspect
from version import Version
from sibs_user import deleteUser

VERSION = Version()
VERSION.register(__name__, REV)

class Service():
    def __init__(self, lou, log):
        self.commands = dict(self.sample_commands())
        self.list_of_implemented_commands = self.list_implemented()
        self.list_of_users = lou
        self.list_of_games = log   # TODO: was besseres als log (log ist logging)
        print 'implemented administrative commands:', self.list_of_implemented_commands

# ----------------------------------------  DB Maintenance

    def a_delete_user(self, line, protocol):
        if len(line) == 1:
            return "** please give a user as an argument."
        kw = {'lou': self.list_of_users, 'user': line[1]}
        return deleteUser(**kw)

    def a_set_field(self, line, protocol):
        fields = ('special', 'password', 'rating', )
        if len(line) < 3 or not line[2] in fields:
            return """** Please give a user and field as an argument.
   Fields are %s.""" % (fields,)
        name = line[1]
        field = line[2]
        args = line[3:]
        user = self.list_of_users.get_from_all(name)
        if user is None:
            return "No user called %s." % name
        config = dict(zip(fields,((1, user.set_special_flag),
                                  (1, user.set_password),
                                  (2, user.set_rating), )))
        nr_args, setter = config[field]
        if len(args) < nr_args:
            return "** Please give %d argument(s) for field %s." % \
                                                           (nr_args, field)
        res = setter(*args)
        return 'set %s for %s to %s' % (field, name, args)

    def a_pack(self, line, protocol):
        arglen = len(line)
        if arglen == 1:
            res = "** please give a DB ('users', 'games') as an argument."
        elif line[1] == 'users':
            self.list_of_users.database.pack()
            res = "probably packed successful"
        elif line[1] == 'games':
            self.list_of_games.database.pack()
            res = "probably packed successful"
        else:
            res = "** please pick one of 'users', 'games'."
        return res

# ----------------------------------------  User Commands

    def a_kick(self, line, protocol):
        arglen = len(line)
        if arglen == 1:
            res = "** please give a name as an argument."
        else:
            user = self.list_of_users.get_active(line[1])
            if user is None:
                res = '** there is noone called %s' % line[1]
            else:
                user.disconnect_hard()
                res = 'kicked %s' % line[1]
        return res

# ----------------------------------------  Community Commands

    def a_nr_users(self, line, protocol):
        return '%s/%s users logged in.' % \
               (self.list_of_users.nr_logged_in(),
                self.list_of_users.nr_registered(),)

# ----------------------------------------  Other Commands

    def a_help(self, line, protocol):
        return '%s' % self.list_of_implemented_commands

    def a_bye(self, line, protocol):
        protocol.logout()

    a_end = a_quit = a_bye

# ----------------------------------------  ====================

    def unknown(self, line, protocol):
        return "** Unknown administrative command: '%s'" % line[0]

    def command(self, cmd):
        return self.commands.get(cmd, self.unknown)

    def sample_commands(self,):
        # TODO: inspect.getmembers() halte ich nicht für der Weisheit letzten
        #       Schluss; vielleicht gibt es da eine bessere (offiziellere) Lösung
        lofc = [(f[0][2:],f[1]) for f in inspect.getmembers(self) \
                  if inspect.ismethod(f[1]) and f[0].startswith('a_')]
        return lofc

    def list_implemented(self, verbose=False):
        imp = self.commands.keys()[:]
        imp.sort()
        for c in imp[:]:
            try:
                ret = self.commands[c]([c,'list',],None)
                if ret.endswith(NYI):
                    imp.remove(c)
            except:
                pass
        return imp

if __name__ == "__main__":
    c = Command(None, None)
    print c.c_version(1,2)
    for i in c.list_implemented():
        print i
