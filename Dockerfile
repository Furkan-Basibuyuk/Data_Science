# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project code into the container
COPY . /app

EXPOSE 3000

# Define environment variables if needed, e.g., for Flask/Dash configurations
# ENV FLASK_ENV=production

# Run the command to start your app (assuming run.py is the entry point)
CMD ["python", "run.py"]
