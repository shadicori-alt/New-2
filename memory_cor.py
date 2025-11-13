# memory_core.py – خفيف (لا يستخدم transformers)
import json, datetime, diskcache as dc

# ذاكرة ملفية خفيفة (حجم كامل < 5 ميجا)
cache = dc.Cache("light_memory", size_limit=50 * 1024 * 1024)   # 50 ميجا كحد أقصى

def save_chat(user_id, question, answer):
    key = f"{user_id}_{datetime.datetime.utcnow().isoformat()}"
    cache[key] = {"q": question, "a": answer, "t": str(datetime.datetime.utcnow())}

def get_chat_history(user_id, last=3):
    keys = [k for k in cache if k.startswith(user_id)]
    keys.sort(reverse=True)
    return [cache[k] for k in keys[:last]]

def search_knowledge(query, top_k=1):
    # بحث بسيط بالكلمات المفتاحية (خفيف وسريع)
    results = []
    for k in cache:
        if query in cache[k]["q"] or query in cache[k]["a"]:
            results.append(cache[k]["a"])
    return results[0] if results else None

def reply_sci(user_id, question):
    history = get_chat_history(user_id)
    context = "\n".join([f"س: {h['q']}\nج: {h['a']}" for h in history])
    ans = search_knowledge(question)
    if ans:
        return f"بناءً على سابقتك:\n{ans}"
    # إذا لم يوجد → نرجع لـ GPT (مُسبقاً مربوط)
    import openai
    openai.api_key = __import__("db").get("openai_key")
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"سؤال محاسبي/إداري: {question}\nالسياق: {context}"}]
    )
    output = res["choices"][0]["message"]["content"]
    save_chat(user_id, question, output)
    return output

def reply_book(user_id, question):
    history = get_chat_history(user_id)
    name = question.split()[0] if question else ""
    return f"أهلاً {name} 💙\nسجلت سؤالك: {question}\nنرجع لك بالتفاصيل والحجز خلال دقائق – فقط اضغط الزر أدناه."