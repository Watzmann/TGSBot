Python 2.6.5 (r265:79063, Apr 16 2010, 13:09:56) 
[GCC 4.4.3] on linux2
Type "copyright", "credits" or "license()" for more information.

    ****************************************************************
    Personal firewall software may warn about the connection IDLE
    makes to its subprocess using this computer's internal loopback
    interface.  This connection is not visible on any external
    interface and no data is sent to or received from the Internet.
    ****************************************************************
    
IDLE 2.6.5      
>>> from persistency import Persistent, Db
>>> db = Db('db/users')
persistency INFO DB:: initializing db/users as default
persistency INFO DB:: opening db/users
>>> db=db.db
>>> t=db['twodice']
>>> t
<sibs_user.Info instance at 0xa44574c>
>>> print t
andreas 1 1 0 1 0 0 1 1 105 0 1 0 1 1480.02 0 0 none 0 0 UTC (kallisto\(2\).fritz.box)
>>> print t.login
1296908012
>>> print t.name
andreas
>>> t.name = 'twodice'
>>> t.name = 'TwoDice'
>>> t.passwd
'andreas'
>>> t.passwd = '2dtest'
>>> print t
TwoDice 1 1 0 1 0 0 1 1 105 0 1 0 1 1480.02 0 0 none 0 0 UTC (kallisto\(2\).fritz.box)
>>> db.sync()
>>> Db('db/users').close()
persistency INFO DB:: initializing db/users as default
persistency INFO DB:: closing db/users
>>> 
