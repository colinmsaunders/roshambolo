#!/usr/bin/python

import os,cgi,sys,hashlib,re,time,cgi

ROOT = '/opt/liarsdice/liarsdice'
LOGS = '/logs'

def register(name,source) :
    sha = hashlib.sha1(source).hexdigest()
    name = 'p_%s_%s' % (re.sub('[^a-z0-9_]','',name),sha[:7])
    f = file('%s/%s.py' % (ROOT,name),'w')
    f.write(source)
    f.close()
    return name

def tournament(games,players) :
    g_id = time.strftime('%Y-%m-%d-%H-%M-%S')
    os.system('/opt/liarsdice/liarsdiceenv/bin/python %s/main.py tournament %d %s > %s/log_%s.txt &' % (ROOT,int(games),' '.join(map(lambda x : re.sub('[^a-z0-9_]','',x),players)),LOGS,g_id))
    return g_id

def game(players) :
    g_id = time.strftime('%Y-%m-%d-%H-%M-%S')
    os.system('/opt/liarsdice/liarsdiceenv/bin/python %s/main.py tournament %d %s > %s/log_%s.txt' % (ROOT,1,' '.join(map(lambda x : re.sub('[^a-z0-9_]','',x),players)),LOGS,g_id))
    output = file('%s/log_%s.txt' % (LOGS,g_id)).read()
    return output

def log(g_id) :
    g_id = re.sub('[^a-z0-9_-]','',g_id)
    for i in file('%s/log_%s.txt' % (LOGS,g_id)).readlines() :
        yield i

def scores(g_id) :
    g_id = re.sub('[^a-z0-9_-]','',g_id)
    for i in file('%s/log_%s.txt' % (LOGS,g_id)).readlines() :
        if -1 == i.find('SCORE') :
            continue
        yield i

def cgimain(args) :

    c = args.get('c')[0]

    if 'register' == c :
        name = args.get('name')[0]
        source = sys.stdin.read()
        x = register(name,source)
        print 'Content-type: text/plain\n\n%s' % x
        sys.exit()

    if 'game' == c :
        players = args.get('players')[0].split(',')
        output = game(players)
        print 'Content-type: text/plain\n\n%s' % output
 
    if 'ping' == c :
        print 'Content-type: text/plain\n\npong'
        sys.exit()

    if 'log' == c :
        g_id = args.get('g_id')[0]
        print 'Content-type: text/plain\n\n'
        for i in log(g_id) :
            sys.stdout.write(i)

    if 'scores' == c :
        g_id = args.get('g_id')[0]
        print 'Content-type: text/plain\n\n'
        for i in scores(g_id) :
            sys.stdout.write(i)

    if 'tournament' == c :
        n = min(10000,int(args.get('n')[0]))
        players = args.get('players')[0].split(',')
        g_id = tournament(n,players)
        print 'Content-type: text/plain\n\n%s' % g_id
 

if __name__ == '__main__' :

    if os.environ.has_key('HTTP_HOST') :
        args = cgi.parse_qs(os.environ.get('QUERY_STRING',''))
        cgimain(args)

    else :
        args = cgi.parse_qs(sys.argv[1])
        cgimain(args)
