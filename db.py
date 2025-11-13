import sqlite3, json, datetime as dt
DB = "data.db"
def conn(): return sqlite3.connect(DB, check_same_thread=False)
def init():
    c = conn()
    c.executescript("""
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS pages(id TEXT PRIMARY KEY, name TEXT, token TEXT, active INT DEFAULT 1);
CREATE TABLE IF NOT EXISTS posts(id TEXT PRIMARY KEY, page_id TEXT, message TEXT, created_at TEXT, reply_template TEXT, dm_template TEXT, active INT DEFAULT 1);
CREATE TABLE IF NOT EXISTS comments(id TEXT PRIMARY KEY, post_id TEXT, from_name TEXT, text TEXT, replied INT DEFAULT 0, created_at TEXT);
CREATE TABLE IF NOT EXISTS inbox(id TEXT PRIMARY KEY, page_id TEXT, user_id TEXT, text TEXT, replied INT DEFAULT 0, created_at TEXT);
CREATE TABLE IF NOT EXISTS welcome_msg(page_id TEXT PRIMARY KEY, text TEXT, buttons TEXT, active INT DEFAULT 1);
CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, customer_name TEXT, phone TEXT, address TEXT, governorate TEXT, notes TEXT, status TEXT DEFAULT "new", agent_id TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS agents(id TEXT PRIMARY KEY, name TEXT, phone TEXT, governorate TEXT, active INT DEFAULT 1);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
INSERT OR IGNORE INTO settings(key,value) VALUES
("admin_pass","1234"),("fb_app_id",""),("fb_app_secret",""),
("google_client_id",""),("google_client_secret",""),
("openai_key",""),("speed_sec","1");
    """)
    c.close()
def get(key):
    c = conn(); val = c.execute("SELECT value FROM settings WHERE key=?",(key,)).fetchone(); c.close()
    return val[0] if val else ""
def set(key,val):
    c = conn(); c.execute("REPLACE INTO settings(key,value)VALUES(?,?)",(key,val)); c.commit(); c.close()
def add_page(pid,name,token):
    c = conn(); c.execute("REPLACE INTO pages(id,name,token)VALUES(?,?,?)",(pid,name,token)); c.commit(); c.close()
def get_pages():
    c = conn(); rows = c.execute("SELECT id,name,token,active FROM pages").fetchall(); c.close(); return rows
def get_posts(page_id=None):
    c = conn()
    if page_id: rows = c.execute("SELECT id,message,reply_template,dm_template,active FROM posts WHERE page_id=?",(page_id,)).fetchall()
    else: rows = c.execute("SELECT id,message,reply_template,dm_template,active FROM posts").fetchall()
    c.close(); return rows
def set_post_templates(pid,reply,dm):
    c = conn(); c.execute("UPDATE posts SET reply_template=?, dm_template=? WHERE id=?",(reply,dm,pid)); c.commit(); c.close()
def add_comment(cid,post_id,from_name,text):
    c = conn(); c.execute("INSERT OR IGNORE INTO comments(id,post_id,from_name,text,created_at)VALUES(?,?,?,?,?)",(cid,post_id,from_name,text,dt.datetime.utcnow().isoformat())); c.commit(); c.close()
def pending_comments():
    c = conn(); rows = c.execute("""SELECT c.id,p.message,c.from_name,c.text FROM comments c JOIN posts p ON c.post_id=p.id WHERE c.replied=0""").fetchall(); c.close(); return rows
def mark_replied(cid): c = conn(); c.execute("UPDATE comments SET replied=1 WHERE id=?",(cid,)); c.commit(); c.close()
def add_inbox(iid,page_id,user_id,text):
    c = conn(); c.execute("INSERT OR IGNORE INTO inbox(id,page_id,user_id,text,created_at)VALUES(?,?,?,?,?)",(iid,page_id,user_id,text,dt.datetime.utcnow().isoformat())); c.commit(); c.close()
def pending_inbox():
    c = conn(); rows = c.execute("SELECT id,page_id,user_id,text FROM inbox WHERE replied=0").fetchall(); c.close(); return rows
def set_welcome(page_id,text,buttons,active):
    c = conn(); c.execute("REPLACE INTO welcome_msg(page_id,text,buttons,active)VALUES(?,?,?,?)",(page_id,text,json.dumps(buttons),active)); c.commit(); c.close()
def get_welcome(page_id):
    c = conn(); row = c.execute("SELECT text,buttons,active FROM welcome_msg WHERE page_id=?",(page_id,)).fetchone(); c.close()
    return (row[0], json.loads(row[1]), row[2]) if row else ("",[],0)
