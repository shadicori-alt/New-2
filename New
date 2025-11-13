#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LastBot-System – ملف الإطلاق الوحيد
بعد التنفيذ يُنشئ كل الملفات ويشغّل الخادم محلياً.
للرفع على Vercel: ارفع المجلد كاملاً بعد التشغيل مرة واحدة (ستجد 8 ملفات داخله).
"""
import os, json, subprocess, shutil, pathlib

# ========== المحتوى الكامل للملفات ==========
FILES = {}

FILES["requirements.txt"] = """Flask==2.3.3
requests==2.31.0
gspread==5.10.0
google-auth==2.22.0
python-dotenv==1.0.0
openai==0.28.1"""

FILES["vercel.json"] = json.dumps({
  "version": 2,
  "builds": [{"src": "app.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "app.py"}]
}, indent=2)

FILES["Dockerfile"] = """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
"""

FILES["db.py"] = '''
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
'''

FILES["core.py"] = '''
import json,requests,threading,datetime as dt
import openai
def fb_get(token,endpoint,params=None):
    url = f"https://graph.facebook.com/v18.0/{endpoint}"
    return requests.get(url,params={**(params or {}),"access_token":token}).json()
def fb_post(token,endpoint,data):
    url = f"https://graph.facebook.com/v18.0/{endpoint}"
    return requests.post(url,data={**data,"access_token":token}).json()
def fb_reply(token,cid,msg): return fb_post(token,f"{cid}/comments",{"message":msg})
def fb_send(token,uid,msg,buttons=None):
    payload = {"recipient":{"id":uid},"message":{"text":msg}}
    if buttons:
        payload["message"]={"attachment":{"type":"template","payload":{"template_type":"button","text":msg,"buttons":[{"type":"web_url","title":b["title"],"url":b["url"]} for b in buttons[:3]]}}}
    return fb_post(token,"me/messages",payload)
def gpt(prompt):
    openai.api_key = __import__("db").get("openai_key")
    if not openai.api_key: return "عذراً، لم يُربط OpenAI."
    return openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role":"user","content":prompt}])["choices"][0]["message"]["content"]
def process_comment(cid,pid,name,text,token):
    import db
    post = db.conn().execute("SELECT reply_template,dm_template FROM posts WHERE id=?",(pid,)).fetchone()
    if not post or not post[0]: return
    reply = post[0].replace("{name}",name)
    if "{ai}" in reply: reply = reply.replace("{ai}",gpt(f"رد قصير ومؤدب على: {text}"))
    fb_reply(token,cid,reply); db.mark_replied(cid)
    dm = post[1]
    if dm:
        user_id = fb_get(token,f"{cid}?fields=from")["from"]["id"]
        dm = dm.replace("{name}",name)
        fb_send(token,user_id,dm)
def process_inbox(iid,page_id,uid,text,token):
    import db
    wt,btns,act = db.get_welcome(page_id)
    if act:
        wt = wt.replace("{name}",text.split()[0] if text else "")
        fb_send(token,uid,wt,btns)
        db.conn().execute("UPDATE inbox SET replied=1 WHERE id=?",(iid,)); db.conn().commit()
'''

FILES["pages.py"] = '''
HTML = {}
HTML["connect"] = """<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>الاتصالات السريعة</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"></head><body class="bg-light">
<div class="container py-4"><h3>اضغط مرة واحدة لكل خدمة</h3>
<a class="btn btn-primary mb-2 d-block" href="/connect/facebook">📘 ربط فيسبوك + ماسنجر + واتساب</a>
<a class="btn btn-success mb-2 d-block" href="/connect/google">📊 ربط جوجل شيت</a>
<a class="btn btn-dark mb-2 d-block" href="/connect/openai">🤖 ربط OpenAI</a>
<hr><a class="btn btn-secondary" href="/">← لوحة التحكم</a></div></body></html>"""

HTML["dashboard"] = """<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>الرئيسية</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{padding-top:1rem}.card{min-height:150px}</style></head><body class="bg-light">
<div class="container"><div class="row g-3">
<div class="col-md-3"><div class="card text-bg-primary"><div class="card-body text-center">
<h5>الصفحات</h5><a class="stretched-link text-white" href="/pages">إدارة</a></div></div></div>
<div class="col-md-3"><div class="card text-bg-success"><div class="card-body text-center">
<h5>المنشورات</h5><a class="stretched-link text-white" href="/posts">الردود</a></div></div></div>
<div class="col-md-3"><div class="card text-bg-info"><div class="card-body text-center">
<h5>التعليقات</h5><a class="stretched-link text-white" href="/comments">مراجعة</a></div></div></div>
<div class="col-md-3"><div class="card text-bg-warning"><div class="card-body text-center">
<h5>الرسائل</h5><a class="stretched-link text-white" href="/inbox">الوارد</a></div></div></div>
<div class="col-md-3"><div class="card text-bg-secondary"><div class="card-body text-center">
<h5>الطلبات</h5><a class="stretched-link text-white" href="/orders">متابعة</a></div></div></div>
<div class="col-md-3"><div class="card text-bg-dark"><div class="card-body text-center">
<h5>المناديب</h5><a class="stretched-link text-white" href="/agents">واجهة الموبايل</a></div></div></div>
<div class="col-md-3"><div class="card text-bg-light"><div class="card-body text-center">
<h5>الإعدادات</h5><a class="stretched-link text-dark" href="/settings">التحكم</a></div></div></div>
<div class="col-md-3"><div class="card text-bg-primary"><div class="card-body text-center">
<h5>الاتصالات</h5><a class="stretched-link text-white" href="/connect">ربط الحسابات</a></div></div></div>
</div></div>
<!-- أيقونة المساعد الذكي -->
<div id="ai-icon"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" width="50"/></div>
<div id="ai-box"><div id="ai-head">المساعد الذكي</div><div id="ai-msgs"></div><input id="ai-inp" placeholder="اسألني..."/></div>
<style>#ai-icon{position:fixed;bottom:20px;right:20px;z-index:9999;cursor:pointer}#ai-box{display:none;position:fixed;bottom:80px;right:20px;width:300px;height:400px;background:#fff;border:1px solid #ccc;border-radius:10px;z-index:9999}#ai-head{background:#007bff;color:#fff;padding:10px;border-radius:10px 10px 0 0}#ai-msgs{height:300px;overflow-y:auto;padding:10px}#ai-inp{width:100%;padding:10px;border:none;border-top:1px solid #ccc}</style>
<script>
document.getElementById("ai-icon").onclick=()=>document.getElementById("ai-box").style.display="block";
document.getElementById("ai-inp").addEventListener("keydown",e=>{
  if(e.key==="Enter"){
    const q=e.target.value,box=document.getElementById("ai-msgs");
    box.innerHTML+=`<div class="text-end"><b>أنت:</b> ${q}</div>`;
    fetch("/api/ask",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({q})})
      .then(r=>r.json()).then(d=>{
        box.innerHTML+=`<div><b>مساعد:</b> ${d.a}</div>`; box.scrollTop=box.scrollHeight;
      });
    e.target.value="";
  }
});
</script>
</body></html>"""

for name,title,url in [("pages","الصفحات","/api/pages"),("posts","المنشورات","/api/posts"),
                      ("comments","التعليقات","/api/comments"),("inbox","الرسائل","/api/inbox"),
                      ("orders","الطلبات","/api/orders"),("agents","المناديب","/api/agents"),
                      ("settings","الإعدادات","/api/settings")]:
    HTML[name] = f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>{title}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"></head><body class="bg-light">
<div class="container py-4"><h3>{title}</h3><div id="cnt"></div>
<button class="btn btn-sm btn-primary" onclick="save()">حفظ</button>
<hr><a class="btn btn-secondary" href="/">← رئيسية</a></div>
<script>async function load(){{cnt.innerHTML=await (await fetch("{url}")).text()}}
async function save(){{alert("يتم الحفظ..."); await fetch("{url}",{{method:"POST",body:new FormData(document.forms[0])}}); load()}}
load()</script></body></html>"""
'''

FILES["app.py"] = '''
from flask import Flask, request, redirect, session, jsonify
import os, json, requests, threading
import db, core, pages

app = Flask(__name__)
app.secret_key = "lastbot-2025"

# Auth
def check_auth():
    if session.get("auth"): return True
    if request.form.get("pass") == db.get("admin_pass"):
        session["auth"] = True
        return True
    return False

# Pages
@app.route("/")
def dash():
    if not check_auth():
        return """<form method="post" class="p-3"><input name="pass" placeholder="كلمة المرور" class="form-control"><button class="btn btn-primary mt-2">دخول</button></form>"""
    return pages.HTML["dashboard"]

@app.route("/connect")
def connect():
    return pages.HTML["connect"]

for route in ["pages","posts","comments","inbox","orders","agents","settings"]:
    exec(f'@app.route("/{route}")\ndef {route}_route(): return pages.HTML["{route}"]')

# OAuth
FB_APP_ID = db.get("fb_app_id")
FB_APP_SECRET = db.get("fb_app_secret")

@app.route("/connect/facebook")
def fb_oauth():
    red = f"{request.scheme}://{request.host}/auth/facebook/callback"
    url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={FB_APP_ID}&redirect_uri={red}&scope=pages_manage_posts,pages_messaging,whatsapp_business_management"
    return redirect(url)

@app.route("/auth/facebook/callback")
def fb_callback():
    code = request.args.get("code")
    red = f"{request.scheme}://{request.host}/auth/facebook/callback"
    r = requests.get("https://graph.facebook.com/v18.0/oauth/access_token", params={
        "client_id": FB_APP_ID, "client_secret": FB_APP_SECRET, "code": code, "redirect_uri": red
    }).json()
    token = r["access_token"]
    pages_data = requests.get(f"https://graph.facebook.com/v18.0/me/accounts?access_token={token}").json()["data"]
    for p in pages_data:
        db.add_page(p["id"], p["name"], p["access_token"])
    return redirect("/pages")

# Webhook
@app.route("/webhook/facebook", methods=["GET", "POST"])
def fb_webhook():
    if request.method == "GET":
        return request.args.get("hub.challenge"), 200
    data = request.get_json()
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") == "feed" and change.get("value", {}).get("item") == "comment":
                v = change["value"]; cid = v["comment_id"]; pid = v["post_id"]; name = v["from"]["name"]; txt = v.get("message", "")
                page_token = db.conn().execute("SELECT token FROM pages WHERE id=?", (v["page_id"],)).fetchone()[0]
                threading.Thread(target=core.process_comment, args=(cid, pid, name, txt, page_token), daemon=True).start()
            if change.get("field") == "messages":
                for msg in entry.get("messaging", []):
                    uid = msg["sender"]["id"]; mid = msg["message"]["mid"]; txt = msg["message"]["text"]
                    page_token = db.conn().execute("SELECT token FROM pages WHERE id=?", (msg["recipient"]["id"],)).fetchone()[0]
                    db.add_inbox(mid, msg["recipient"]["id"], uid, txt)
                    threading.Thread(target=core.process_inbox, args=(mid, msg["recipient"]["id"], uid, txt, page_token), daemon=True).start()
    return "OK", 200

# API
for ep in ["pages","posts","comments","inbox","orders","agents","settings"]:
    exec(f'''
@app.route("/api/{ep}", methods=["GET","POST"])
def api_{ep}():
    if request.method=="POST":
        # يمكنك لاحقاً إضافة منطق الحفظ هنا
        pass
    rows = []  # placeholder
    return jsonify(rows)
''')

@app.route("/api/ask", methods=["POST"])
def ask():
    q = request.get_json().get("q", "")
    a = core.gpt(q)
    return jsonify({"a": a})

# تشغيل الخادم
if __name__ == "__main__":
    db.init()
    app.run(host="0.0.0.0", port=5000, debug=True)
'''

# static_pack.py
FILES["static_pack.py"] = '''
# مضغوط داخل pages و app
'''

# ====== إنشاء الملفات وتشغيل المحلي ======
def install_and_run():
    for name, content in FILES.items():
        with open(name, "w", encoding="utf-8") as f:
            f.write(content.strip())
    print("✅ تم إنشاء كل الملفات.")
    os.system("pip install -r requirements.txt")
    print("🚀 تشغيل الخادم الآن ...")
    os.system("flask --app app.py run")

if __name__ == "__main__":
    install_and_run()
