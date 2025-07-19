# Use a slim Python image
FROM python:3.11-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the rest of your application code, including alembic.ini and migrations folder
# The '.' at the end means "copy to the current working directory (/app)"
COPY . .

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:app"]