# Coding Platform with AI Hints

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MySQL](https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![GitHub issues](https://img.shields.io/github/issues/vinayvinu500/Coding-Platform.git)
![GitHub forks](https://img.shields.io/github/forks/vinayvinu500/Coding-Platform.git)
![GitHub stars](https://img.shields.io/github/stars/vinayvinu500/Coding-Platform.git)
![GitHub license](https://img.shields.io/github/license/vinayvinu500/Coding-Platform.git)

**Coding Platform with AI Hints** is a modern web application designed to enhance the SQL learning experience through real-time coding environments, AI-generated hints, and interactive problem-solving. Built on FastAPI and leveraging both MySQL and SQLite databases, this platform offers a seamless backend service with asynchronous RESTful API support. It integrates Google API/OpenAI API for generating AI hints, making SQL learning intuitive and engaging.

## Technologies Used

- **Frontend:** HTML, CSS, JavaScript
  - **Templating Engine:** Jinja2 for dynamic server-side rendering
  - **Styling:** Custom CSS and responsive design principles
  - **Client-Side Logic:** Vanilla JavaScript for dynamic content manipulation and API interactions

- **Backend:** FastAPI
  - **Database Management:** SQLite (for user authentication and management), MySQL (for SQL coding environment)
  - **Authentication:** JWT tokens for secure user sessions
  - **APIs:** Integration with Google API and OpenAI for generating AI-based hints

## Features

- **Interactive Coding Environment:** Users can write, test, and get hints for SQL queries within a dedicated coding workspace.
- **Dynamic Content Rendering:** Utilizes Jinja2 templating engine alongside client-side JavaScript to render dynamic content and create an interactive user experience.
- **AI-Generated Hints:** Stuck on a problem? Get AI-powered hints to guide you towards the solution.
- **Authentication & Security:** Secure login and authentication system with JWT token support. Passwords are hashed and salted then stored in SQLite database for enhanced security.
- **Extensive Question Library:** Access a wide range of SQL problems, from beginner to advanced levels.
- **Create & Share:** Contribute to the community by creating and sharing your SQL challenges. Users can view a list of available questions, create new questions, and navigate through them seamlessly.

## Getting Started

To set up and run the SQL Coding Platform locally, follow these steps:


1. **Clone the Repository:**
    ```bash
    git init
    git clone https://github.com/vinayvinu500/Coding-Platform.git
    cd Coding-Platform
    ```

2. **Install Dependencies:**
   Ensure you have Python 3.8+ installed. Then install the required Python packages using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   Access the platform at `http://localhost:8000`.

### Usage

1. **Login/Signup:** Navigate to `localhost:8000` and enter your credentials to start.
2. **Browse Questions:** Access `localhost:8000/questions-list` to explore the SQL challenges.
3. **Coding Environment:** Select a problem or create a new one at `localhost:8000/create-question`. Test your queries and request AI hints in the coding environment.
4. **View Solutions:** By visiting `localhost:8000/question/1` and check your solutions against provided questions and hints for learning and improvement.

## Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit pull requests to the project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- AI Hints powered by [OpenAI](https://openai.com/)
- Backend API documentation generated with [FastAPI](https://fastapi.tiangolo.com/)
- The SQL learning community for continuous support and feedback

## Contact

Your Name - [@VinayGovardhanam](https://www.linkedin.com/in/vinay-govardhanam-a21213183/)

Project Link: [https://github.com/vinayvinu500/Coding-Platform.git](https://github.com/vinayvinu500/Coding-Platform.git)