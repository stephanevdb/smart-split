# Use Python 3.11 slim image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 5000

# Run the Flask application using Gunicorn
# 'app:app' means: look for a file named 'app.py' and within it, find a Flask instance named 'app'.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
