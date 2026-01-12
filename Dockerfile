# 1️⃣ Base image خفيفة وآمنة
FROM python:3.9-slim

# 2️⃣ منع تشغيل التطبيق ب root
RUN useradd -m appuser

# 3️⃣ تحديد مجلد العمل
WORKDIR /app

# 4️⃣ نسخ requirements فقط (best practice)
COPY requirements.txt .

# 5️⃣ تثبيت dependencies بلا cache
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ نسخ الكود
COPY api/ .

# 7️⃣ Permissions
RUN chown -R appuser:appuser /app

# 8️⃣ Switch user
USER appuser

# 9️⃣ Port
EXPOSE 5000

# 🔟 Run app
CMD ["python", "app.py"]
