# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Copy the current directory contents into the container
COPY . .

RUN mkdir /origin && mkdir /destination

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "main.py"]
