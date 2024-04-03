// Initialize Ace editors and Jodit editor upon DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {

  // async function validateToken(token) {
  //   try {
  //     const response = await fetch("/api/token/validate", {
  //       method: "GET", // or GET, depending on how you set it up
  //       headers: {
  //         Authorization: `Bearer ${token}`,
  //       },
  //     });
  //     if (response.ok) {
  //       const data = await response.json();
  //       return data.isValid;
  //     }
  //     throw new Error("Token validation failed");
  //   } catch (error) {
  //     console.error("Error validating token:", error);
  //     return false;
  //   }
  // }

  // const token = localStorage.getItem("token");
  // if (!token) {
  //   // Redirect to login if no token found
  //   window.location.href = "/";
  // } else {
  //   // Optional: You could validate the token against a backend endpoint
  //   validateToken(token).then((isValid) => {
  //     if (!isValid) {
  //       window.location.href = "/";
  //     }
  //   });
  // }

  initializeEditors();
  setupEventListeners();

  const schemaFileSelector = document.getElementById("schema-file-selector");
  schemaFileSelector.addEventListener("change", async function () {
    const fileName = this.value;
    if (fileName) {
      // If a file is selected, fetch and display its content
      const fileContent = await fetchSchemaFileContent(fileName);
      window["db-schema-editor"].setValue(fileContent, -1);
    } else {
      // If no file is selected (zero state), clear the editor
      window["db-schema-editor"].setValue("");
    }
  });

  // Assuming you have a form with the ID 'content-form'
  const form = document.getElementById("content-form");
  const testButton = document.getElementById("test-btn");

  form.addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent the default form submission
    await submitQuestion(); // Call your submit function
  });

  testButton.addEventListener("click", async () => {
    await testQuery(); // Call your test function
  });
});


function initializeEditors() {
  // Initialize Ace Editors
  const aceEditorIds = ["db-schema-editor", "user-query", "sample-solution"];
  const initialValue = "-- write your query below\n"; // Predefined value to set in each editor
  aceEditorIds.forEach(
    (id) => {
      const editor = ace.edit(id);
      editor.setTheme("ace/theme/monokai");
      editor.session.setMode("ace/mode/sql");
      editor.setShowPrintMargin(false);
      editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
      });
      editor.setValue(initialValue, -1); // Set predefined value for each editor
      editor.clearSelection(); // This will remove the highlight over the text
      editor.setValue(initialValue, 1); // moves cursor to the end
      // editor.navigateToEnd(); // Move cursor to the end of the editor content // side effects like not visible of sample-solution and user-query
      editor.resize(); // Refresh editor's layout
      window[id] = editor; // Make editor accessible globally
    },
    { passive: true }
  );

  // Initialize Jodit Editor
  window.joditEditor = new Jodit("#editor", {
    // Jodit options here
    height: 600,
    buttons: [
      "bold",
      "italic",
      "underline",
      "strikethrough",
      "|",
      "ul",
      "ol",
      "|",
      "outdent",
      "indent",
      "|",
      "font",
      "fontsize",
      "brush",
      "paragraph",
      "|",
      "image",
      "table",
      "link",
      "|",
      "align",
      "undo",
      "redo",
      "\n",
      "selectall",
      "cut",
      "copy",
      "paste",
    ],
  });
}

async function fetchSchemaFileContent(fileName) {
  try {
    const response = await fetch(`/schema-content/${fileName}`);
    if (!response.ok) throw new Error("Failed to load schema file content");
    return await response.text();
  } catch (error) {
    console.error("Failed to fetch schema file content:", error);
    return ""; // Return empty string on failure
  }
}

function setupEventListeners() {
  // Directly attach testQuery to the test button
  document
    .getElementById("test-btn")
    .addEventListener("click", async (event) => {
      event.preventDefault();
      await testQuery();
    });

  // If you have a specific function for submit, attach it here
  // Assuming submitQuestion() is defined similarly to testQuery()
  document
    .getElementById("submit-btn")
    .addEventListener("click", async (event) => {
      event.preventDefault();
      await submitQuestion();
    });
}

async function testQuery() {
  const databaseSchema = window["db-schema-editor"].getValue();
  const sampleSolution = window["sample-solution"].getValue();
  const defaultMsg = "-- write your query below\n"; // Assume this is your default message in Ace Editor
  const token = localStorage.getItem("token");

  // Function to check if the entire code is commented or equals the default message
  function isCodeInvalid(code) {
    // Check if the code is just the default message or empty
    if (!code.trim() || code.trim() === defaultMsg) {
      return true;
    }
    // Check if the entire code is commented out
    const lines = code
      .trim()
      .split("\n")
      .filter((line) => line.trim());
    if (lines.every((line) => line.startsWith("--"))) {
      // Assuming SQL comment syntax for simplicity
      return true;
    }
    return false;
  }

  // Validate input
  if (isCodeInvalid(databaseSchema) || isCodeInvalid(sampleSolution)) {
    const resultsContainer = document.getElementById("test-results");
    resultsContainer.innerHTML =
      "<p class='error'>Both database schema and sample solution are required and must contain valid SQL code.</p>";
    window.isTestSuccessful = false;
    return; // Stop the function execution if validation fails
  }

  const requestBody = {
    database_schema: databaseSchema,
    sample_solution: sampleSolution,
  };

  try {
    const response = await fetch("/test-query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    });
    const data = await response.json(); // Parse the JSON body first to handle both success and error cases uniformly.
    if (!response.ok) {
      // Use the detailed error message from the backend if available.
      const errorMessage =
        data && data.error
          ? data.error
          : `"An unknown error occurred: ${data}"`;
      const resultsContainer = document.getElementById("test-results");
      resultsContainer.innerHTML = ""; // Clear previous results.
      resultsContainer.innerHTML = `<p class="error">${errorMessage}</p>`;
      window.isTestSuccessful = false;
      throw new Error(errorMessage);
    }

    displayTestResults(data); // Handle displaying of results or errors.
    window.isTestSuccessful = true;
  } catch (error) {
    const resultsContainer = document.getElementById("test-results");
    resultsContainer.innerHTML = ""; // Clear previous results.
    resultsContainer.innerHTML = `<p class="error">${error.message}</p>`;
    window.isTestSuccessful = false;
  }
}

function displayTestResults(data) {
  const resultsContainer = document.getElementById("test-results");
  resultsContainer.innerHTML = ""; // Clear previous results

  if (data.error) {
    // Display error message
    const errorMessage = document.createElement("p");
    errorMessage.className = "error"; // Apply the .error class for styling
    errorMessage.textContent = `Test Failed: ${data.error}`;
    resultsContainer.appendChild(errorMessage);
  } else if (data.results && data.results.length > 0) {
    // Display success message
    const successMessage = document.createElement("p");
    successMessage.className = "success";
    successMessage.textContent = "Test Successful";
    resultsContainer.appendChild(successMessage);

    // Continue with creating and appending the table
    const table = document.createElement("table");
    table.className = "results-table";

    const thead = table.createTHead();
    const headerRow = thead.insertRow();
    const headers = Object.keys(data.results[0]);
    headers.forEach((header) => {
      const th = document.createElement("th");
      th.textContent = header;
      th.style.textAlign = "center";
      headerRow.appendChild(th);
    });

    const tbody = table.createTBody();
    data.results.forEach((row) => {
      const tableRow = tbody.insertRow();
      headers.forEach((header) => {
        const cell = tableRow.insertCell();
        cell.textContent = row[header];
        cell.style.textAlign = "center";
      });
    });

    resultsContainer.appendChild(table);
  } else {
    const errorMessage = document.createElement("p");
    errorMessage.className = "error"; // Apply the .error class for styling
    errorMessage.textContent = `Test Failed: No results found.`;
    resultsContainer.appendChild(errorMessage);
    // resultsContainer.innerHTML = `<p>No results found.</p>`;
  }

  resultsContainer.scrollIntoView({ behavior: "smooth", block: "end" });
}

async function submitQuestion() {
  const title = document.getElementById("problem-title").value;
  const description = window.joditEditor.value; // Assuming Jodit editor's instance is named joditEditor
  const databaseSchema = window["db-schema-editor"].getSession().getValue();
  const sampleSolution = window["sample-solution"].getSession().getValue();
  const userQuery = window["user-query"].getSession().getValue(); // Assuming user query is optional
  const difficultLevel = document.getElementById("difficulty-selector").value;
  const selectedFile = document.getElementById("schema-file-selector").value;
  const newFileName = document.getElementById("schema-file-name").value.trim();
  const token = localStorage.getItem("token");

  // Function to check for default message, emptiness, or fully commented out code in Ace Editors
  function isInvalidCode(code) {
    const defaultMsg = "-- write your query below\n";
    return (
      !code.trim() ||
      code.trim() === defaultMsg ||
      code
        .trim()
        .split("\n")
        .every((line) => line.trim().startsWith("--"))
    );
  }

  // Validate required fields
  if (!title || !description.trim()) {
    alert("Title and problem description are required.");
    return;
  }

  // Validate Ace Editor fields
  if (isInvalidCode(databaseSchema) || isInvalidCode(sampleSolution)) {
    alert("Database schema and sample solution must contain valid SQL code.");
    return;
  }

  // Validate file selection or new file name entry if database schema is used
  if (databaseSchema && !selectedFile && !newFileName) {
    alert(
      "Please select an existing schema file or enter a new file name for the database schema."
    );
    return;
  }

  // Check if the test was successful
  if (!window.isTestSuccessful) {
    alert("Please successfully test your query before submitting.");
    return;
  }

  // Construct the requestBody for submission
  const requestBody = {
    title,
    description,
    difficultLevel,
    fileName: newFileName || selectedFile,
    databaseSchema,
    userQuery, // Assuming it's optional
    sampleSolution,
  };

  try {
    const response = await fetch("/submit-question", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    });

    // Check if the submission was successful
    if (response.ok) {
      // If you're expecting a JSON response, parse it
      // const responseData = await response.json();

      // Redirect to the questions list or another page based on your logic
      window.location.href = "/questions-list";
    } else {
      // Handle server-side validation errors or other issues
      const errorData = await response.json();
      alert(`Submission failed: ${errorData.detail}`);
    }
  } catch (error) {
    // Handle network errors or problems with the fetch operation
    console.error(`Submission failed: ${error}`);
    alert("Submission failed. Please try again.");
  }
}

document
  .getElementById("content-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent the traditional form submission
    await submitQuestion();
  });
