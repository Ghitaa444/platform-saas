# Use the official Python image as a base
FROM python:3.11-slim-buster

# Set the working directory to /app inside the container.
WORKDIR /app

# Copy the entire project directory into the container.
COPY . .

# Set the PYTHONPATH to include the /app directory.
ENV PYTHONPATH=/app

# Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on.
EXPOSE 5000

# Set the FLASK_APP environment variable.
ENV FLASK_APP=backend/app.py

# Run the application with Gunicorn.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "backend.app:app"]