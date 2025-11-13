# ==========================================
# core.py – أوامر Facebook + OpenAI + الذاكرة المشتركة
# ==========================================
import json, requests, threading, datetime
import openai
import memory_core as mem   # <<< الذاكرة المشتركة الجديدة

# ========== إعدادات عامة ==========
FB_APP_ID     = __import__("db").get("fb_app_id")
FB_APP_SECRET = __import__("db").get("fb_app_secret")
OPENAI_KEY    = __import__("db").get("openai_key")
SPEED_SEC     = int(__import__("db").get("speed_sec") or 1)

# ========== أوامر Facebook ==========
def fb_get(token, endpoint, params=None):
    url = f"https://graph.facebook.com/v18.0/{endpoint}"
    return requests.get(url, params={**(params or {}), "access_token": token}).json()

def fb_post(token, endpoint, data):
    url = f"https://graph.facebook.com/v18.0/{endpoint}"
    return requests.post(url, data={**data, "access_token": token}).json()

def fb_reply_comment(token, comment_id, message):
    return fb_post(token, f"{comment_id}/comments", {"message": message})

def fb_send_msg(token, user_id, message, buttons=None):
    payload = {"recipient": {"id": user_id}, "message": {"text": message}}
    if buttons:
        payload["message"] = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": message,
                    "buttons": [{"type": "web_url", "title": b["title"], "url": b["url"]} for b in buttons[:3]]
                }
            }
        }
    return fb_post(token, "me/messages", payload)

# ========== أوامر OpenAI ==========
def gpt(prompt):
    openai.api_key = OPENAI_KEY
    if not openai.api_key:
        return "عذراً، لم يُربط OpenAI."
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res["choices"][0]["message"]["content"]

# ========== الذاكرة المشتركة (علمي + حجز) ==========
def process_with_memory(user_id, question, mode="sci"):
    """mode='sci' → رد علمي مفصل  
       mode='book' → رد حجز لطيف"""
    if mode == "sci":
        return mem.reply_sci(user_id, question)
    return mem.reply_book(user_id, question)

# ========== معالجة التعليقات (مع الذاكرة) ==========
def process_comment(comment_id, post_id, from_name, text, token):
    import db
    post = db.conn().execute("SELECT reply_template, dm_template FROM posts WHERE id=?", (post_id,)).fetchone()
    if not post or not post[0]:
        return

    reply = post[0].replace("{name}", from_name)

    # استبدال متغيرات الذاكرة الجديدة
    if "{ai_sci}" in reply:
        reply = reply.replace("{ai_sci}", process_with_memory(from_name, text, "sci"))
    if "{ai_book}" in reply:
        reply = reply.replace("{ai_book}", process_with_memory(from_name, text, "book"))
    if "{ai}" in reply:
        reply = reply.replace("{ai}", gpt(f"رد قصير ومؤدب على: {text}"))

    fb_reply_comment(token, comment_id, reply)
    db.mark_replied(comment_id)

    # رسالة خاصة بالعميل (مرة واحدة)
    dm = post[1]
    if dm:
        user_id = fb_get(token, f"{comment_id}?fields=from")["from"]["id"]
        dm = dm.replace("{name}", from_name)
        fb_send_msg(token, user_id, dm)

# ========== معالجة الرسائل الواردة (مع الذاكرة) ==========
def process_inbox(msg_id, page_id, user_id, text, token):
    import db
    welcome_text, buttons, active = db.get_welcome(page_id)
    if active:
        welcome = welcome_text.replace("{name}", text.split()[0] if text else "")

        # يمكنك استخدام الذاكرة هنا أيضاً إذا أردت
        if "{ai_sci}" in welcome:
            welcome = welcome.replace("{ai_sci}", process_with_memory(user_id, text, "sci"))
        if "{ai_book}" in welcome:
            welcome = welcome.replace("{ai_book}", process_with_memory(user_id, text, "book"))

        fb_send_msg(token, user_id, welcome, buttons)
        db.conn().execute("UPDATE inbox SET replied=1 WHERE id=?", (msg_id,))
        db.conn().commit()
