# Flask and MySQL Application with Docker

This project sets up a Flask application connected to a MySQL database, both running in Docker containers. The setup avoids port conflicts with local MySQL instances by mapping the MySQL container's port to a non-default port on the host machine.

## Project Structure
```fs
demo/
├── .env                   # Environment variables for MySQL configuration
├── docker-compose.yml     # Defines the services, networks, and volumes
├── database/
│   ├── Dockerfile         # Builds the MySQL database container
│   └── database_schema.sql # SQL schema for initializing the database
└── server/
    ├── Dockerfile         # Builds the Flask application container
    ├── main.py            # Flask application entry point
    ├── requirements.txt   # Python dependencies
    └── wait-for-it.sh     # Script to wait for the database to be ready
```

## Prerequisites

- Docker and Docker Compose installed on your machine.
- Basic understanding of Docker, Flask, and MySQL.

## Configuration

1. **Environment Variables**: The `.env` file contains MySQL configuration variables. Example:
```.env
MYSQL_DATABASE=testing 
MYSQL_ROOT_USER=root 
MYSQL_ROOT_PASSWORD=password
```

2. **Port Configuration**: To avoid conflicts with local MySQL instances, the MySQL container's port `3306` is mapped to `3307` on the host.

## How to Run

1. **Build and Run Containers**: Navigate to the project root directory and execute:

```bash
docker-compose up --build
```
This command builds the images for both the Flask application and MySQL database, and starts the containers.


- Access the Application: Once the containers are up, access the Flask application by navigating to http://localhost:8000 in your browser.

## Interacting with the Database
The Flask application connects to the MySQL database using the configuration specified in the .env file and main.py. Ensure that any database interactions in your Flask application use the correct database configuration.

## Customizations
- ***MySQL Port***: If you wish to change the MySQL container's external port, update the ports section in docker-compose.yml and adjust the port parameter in main.py accordingly.

- ***Database Schema***: Modify database_schema.sql to customize the database schema according to your application's requirements.

## Troubleshooting
- ***Database Connection Issues***: If the Flask application cannot connect to the MySQL database, ensure the MySQL container is fully initialized before the Flask application starts. Adjustments can be made in the wait-for-it.sh script command within docker-compose.yml.

## Contributing
Contributions to improve the project are welcome. Please follow the standard fork and pull request workflow.