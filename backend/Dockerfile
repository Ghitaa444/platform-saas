# ✅ Use official Python image
FROM python:3.11-slim-buster

# ✅ Set working directory
WORKDIR /app

# ✅ Copy backend files only
COPY backend/ ./

# ✅ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Expose Flask port
EXPOSE 5000

# ✅ Environment vars
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py

# ✅ Run with Gunicorn (with gevent)
RUN pip install gevent gunicorn
CMD ["gunicorn", "--worker-class", "gevent", "--timeout", "120", "--bind", "0.0.0.0:5000", "app:app"]
