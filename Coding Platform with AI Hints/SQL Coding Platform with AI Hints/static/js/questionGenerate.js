document.addEventListener("DOMContentLoaded", (event) => {
  document
    .getElementById("generateQuestionsButton")
    .addEventListener("click", generateQuestions);
});

function generateQuestions() {
  // Prevent default form submission if necessary
  // event.preventDefault(); // Uncomment this line if your button has type="submit"
  // Attempt to retrieve the token from localStorage
  const token = localStorage.getItem("token"); // Adjust 'jwtToken' based on your storage key

  if (!token) {
    console.error("Authorization token not found. Please log in.");
    return; // Stop the function if no token is found
  }

  // Get the form data
  const language = document.getElementById("languageSelect").value;
  const numQuestions = parseInt(
    document.getElementById("numQuestions").value,
    10
  ); // Ensure this is an integer
  const topic = document.getElementById("topicInput").value.trim(); // Trim whitespace just in case
  
  // function mapDifficultyToNumber(difficulty) {
  //   switch (difficulty) {
  //     case "Easy":
  //       return 1;
  //     case "Medium":
  //       return 2;
  //     case "Hard":
  //       return 3;
  //     default:
  //       return 1; // Default to 1 (Easy) if unexpected value
  //   }
  // }

  // Inside your generateQuestions function:
  // const difficulty = mapDifficultyToNumber(
  //   document.getElementById("difficultySelect").value
  // );
  const difficulty = document.getElementById("difficultySelect").value;


  // Construct the request body
  const requestBody = {
    language: language,
    num_questions: numQuestions,
    topic: topic,
    difficulty_level: difficulty,
  };
  
  // Send the data to the FastAPI backend
  fetch("/generate-questions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(requestBody),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json(); // Here we assume the server will return JSON; adjust if different
    })
    .then((data) => {
      console.log(data);
      // Here you would handle the response and update the UI accordingly
    })
    .catch((error) => {
      console.error(
        "There has been a problem with your fetch operation:",
        error
      );
      // Handle the error
    });
}
