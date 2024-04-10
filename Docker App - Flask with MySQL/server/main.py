from flask import Flask, jsonify
import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv(), override=True)
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def get_mysql_connection():
    """Function to connect to the MySQL database and return the connection."""
    try:
        connection = mysql.connector.connect(
            host='database',         # e.g., 'localhost'
            port=3306,
            database=os.environ.get("MYSQL_DATABASE"), # your database name
            user=os.environ.get("MYSQL_ROOT_USER"),     # your database username
            password= os.environ.get("MYSQL_ROOT_PASSWORD")  # your database password
        )
        return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

@app.route('/')
def hello_world():
    return jsonify({"message": "Hello World!"})

@app.route('/data')
def get_data():
    """Endpoint to fetch data from MySQL database."""
    try:
        conn = get_mysql_connection()
        if conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM passenger;") # Replace 'your_table_name' with your table name
            records = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify(records)
    except Error as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8000, host='0.0.0.0') 
    # python main.py
    # gunicorn --bind 0.0.0.0:8080 -w 5 main:app
    # pip freeze > requirements.txt
    # waitress.serve(app, listen='0.0.0.0:5003')
    # waitress-serve --listen=127.0.0.1:8080 myapp.wsgi:application
    # CMD ["waitress-serve", "--listen=127.0.0.1:8080", "main:app"]
    # docker build -t flask-app .
    # docker images # list of images
    # docker run d -p 8080:8080 flask-app
    # docker logs <container-id>
    # dockers ps # list of running containers
    # docker run -it --rm --name mysql-dev -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
    # docker exec -it mysql-dev bash