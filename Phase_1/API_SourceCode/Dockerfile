# Set base image (host OS)
FROM python:3.10.2

# By default, Listen on port 8000
EXPOSE 8000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the workin directory
COPY api.py .

# Specify the command to run on container start
CMD [ "python", "./api.py" ]