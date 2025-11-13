import json, datetime
from sentence_transformers import SentenceTransformer
from chromadb import Client, Settings
from transformers import pipeline

model = SentenceTransformer("aubmindlab/bert-base-arabertv02")
chroma_client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="chroma_data"))
collection = chroma_client.get_or_create_collection("biz_memory")
chat_memory = {}

def save_chat(user_id, question, answer):
    chat_memory[user_id] = chat_memory.get(user_id, []) + [{"q": question, "a": answer, "t": str(datetime.datetime.utcnow())}]
    vector = model.encode(question).tolist()
    collection.add(embeddings=[vector], documents=[json.dumps({"q": question, "a": answer}, ensure_ascii=False)], metadatas=[{"user": user_id, "t": str(datetime.datetime.utcnow())}], ids=[f"{user_id}_{len(chat_memory[user_id])}"])

def get_chat_history(user_id, last=3):
    return chat_memory.get(user_id, [])[-last:]

def search_knowledge(query, top_k=1):
    vector = model.encode(query).tolist()
    docs = collection.query(query_embeddings=[vector], n_results=top_k)
    if docs["documents"]:
        return json.loads(docs["documents"][0][0])["a"]
    return None

def reply_sci(user_id, question):
    history = get_chat_history(user_id)
    context = "\n".join([f"س: {h['q']}\nج: {h['a']}" for h in history])
    ans = search_knowledge(question)
    if ans:
        return f"بناءً على سابقتك:\n{ans}"
    generator = pipeline("text2text-generation", model="aubmindlab/bert-base-arabertv02")
    prompt = f"سؤال محاسبي/إداري: {question}\nالسياق: {context}\nالإجابة العلمية المفصلة:"
    output = generator(prompt, max_length=250, do_sample=False)[0]["generated_text"]
    save_chat(user_id, question, output)
    return output

def reply_book(user_id, question):
    history = get_chat_history(user_id)
    name = question.split()[0] if question else ""
    return f"أهلاً {name} 💙\nسجلت سؤالك: {question}\nنرجع لك بالتفاصيل والحجز خلال دقائق – فقط اضغط الزر أدناه."
