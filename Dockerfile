# Use the official Python image (full version) as a base
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (optional for Heroku, as it's dynamically assigned)
EXPOSE 5000

# Run the Flask server and bot when the container starts
CMD ["python", "main.py"]
