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
</body></html>"""

for name,title,url in [("pages","الصفحات","/api/pages"),("posts","ال
