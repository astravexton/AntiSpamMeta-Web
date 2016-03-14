from peewee import MySQLDatabase
from pymysql import err
import web

host = "CHANGEME"
user = "CHANGEME"
passwd = "CHANGEME"

web.config.debug = False

urls = (
    "/",            "index",
    "/investigate", "index",
)
app = web.application(urls, globals())

render = web.template.render("templates/")

class index:        
    def GET(self):
        i = web.input(nickname=None, user=None, hostname=None, account=None, gecos=None)
        try:
            results = doSQL(i.nickname, i.user, i.hostname, i.account, i.gecos)
        except err.ProgrammingError:
            results = ""
        yield render.form(results)

if __name__ == "__main__":
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()

def doSQL(n, u, h, a, g):
    db = MySQLDatabase("asm_main", host=host, port=3306, user=user, passwd=passwd)
    db.connect()
    cur = db.get_cursor()
    
    nick = n
    user = u
    host = h
    account = a
    gecos = g
    
    escape = db.get_conn().escape_string
    
    sql = "SELECT * FROM actionlog WHERE "
    search = []
    if nick:
        search.append("nick LIKE '{nick}'".format(nick=escape(nick)))
    if user:
        search.append("user LIKE '{user}'".format(user=escape(user)))
    if host:
        search.append("host LIKE '{host}'".format(host=escape(host)))
    if account:
        search.append("account LIKE '{account}'".format(account=escape(account)))
    if gecos:
        search.append("gecos LIKE '{gecos}'".format(gecos=escape(gecos)))
    
    sql = sql+" OR ".join(search)
    l = cur.execute(sql)
    output = ""
    for row in cur.fetchall():
        output+= "<tr>"
        output+= "<td>#{}</td>".format(row[0]) # id
        output+= "<td>{}</td>".format(row[1])  # date
        output+= "<td>{}<span class=\"userhost\">!{}@{}</span></td>".format(row[5],row[6],row[7]) # nick!ident@host
        output+= "<td>received {}".format(row[2])  # event
        # (11, datetime.datetime(2016, 2, 21, 20, 25, 45), 'quiet', None, '##doge', 'doge', '~doge',
        # 'antispammeta/suchmeta/botters.doge', None, 'doge', 'doge', 'falco-devel', '~falco',
        # 'botters/doge/bot/falco', "nathan's bot", 'falco')
        if row[11]:
            output+= " from {}<span class=\"userhost\">{}{}</span></td>".format(
                row[11], "!"+row[12] if row[12] else "", "@"+row[13] if row[13] else "") # who it was from
        output+= "<td>{}</td>".format(row[4] if row[4] else "") # channel
        output+= "<td>{}</td>".format(row[3] if row[3] else "") # reason
        output+= "</tr>"
    return output
