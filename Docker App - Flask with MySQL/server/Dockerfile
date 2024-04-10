FROM python:3.11

WORKDIR /app

# Copy the application files
COPY ./requirements.txt .
COPY ./main.py .
COPY ./wait-for-it.sh ./wait-for-it.sh

# Install dependencies
RUN pip3 install -r requirements.txt

# Make wait-for-it.sh executable
RUN chmod +x ./wait-for-it.sh

# Extra checks
EXPOSE 8000

# CMD ["gunicorn", "-b 0.0.0.0:8000", "-w 5", "main:app"]

# docker run -it -d -p 8000:8000 flask-app:latest