import os,sys,time,urllib2,json,re

def get_lock() :
    while 1 :
        try :
            f = file('director.lock','r')
            f.close()
            time.sleep(1.0)
            continue
        except :
            f = file('director.lock','w')
            f.close()
            return

def release_lock() :
    os.remove('director.lock')

def slack_message(s) :
    payload = {}
    payload['channel'] = '#liarsdice'
    payload['username'] = 'tournament_director'
    payload['icon_emoji'] = ':game_die:'
    payload['text'] = s
    url_slack_webhook = 'https://surveymonkey.slack.com/services/hooks/incoming-webhook?token=viiX33zJyHusnVq9xK6zQx4f'
    req = urllib2.Request(url_slack_webhook,json.dumps(payload))
    urllib2.urlopen(req).read()
    pass

def tournament(n,log,players) :
    get_lock()
    f = file(log,'w')
    fo = os.popen('python main.py tournament %d %s' % (n,' '.join(players)))
    a = []
    for i in fo.readlines() :
        f.write(i)
        m = re.match('^.*INFO\\s+SCORE$',i)
        if None != m :
            if 0 != len(a) :
                x = int(a[0][:a[0].find(' ')])
                if 0 == (x % 1000) :
                    message = '\n'.join(a)
                    slack_message(message)
            a = []
        m = re.match('^.*INFO\\s+SCORE.game.(\\d+).of.(\\d+).(.*)$',i)
        if None != m :
            g = m.groups()
            a.append('%s of %s -- %s' % (g[0],g[1],g[2]))
    f.close()
    release_lock()
 
if __name__ == '__main__' :

    if 'get_lock' == sys.argv[1] :
        get_lock()

    if 'slack' == sys.argv[1] :
        slack_message(sys.argv[2])

    if 'tournament' == sys.argv[1] :
        n = int(sys.argv[2])
        log = sys.argv[3]
        players = sys.argv[4:]
        tournament(n,log,players)

