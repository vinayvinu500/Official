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

  // Initialize Ace Editor
  var editor = ace.edit("code-editor");
  editor.setTheme("ace/theme/monokai"); // editor.setTheme("ace/theme/twilight");
  editor.session.setMode("ace/mode/sql");
  editor.setShowPrintMargin(false);

  // Set the editor content
  // var userQuery = `"{{ question.UserQuery }}"`; // Use tojson and safe filters for correct JSON string
  // var userQuery = editor.container.question.UserQuery || "not resolved"; // Fetching the user query from data attribute
  // var userQuery = editor.container.dataset.userQuery || ""; // Fetching the user query from data attribute
  editor.session.setValue(userQuery, -1);
  editor.clearSelection(); // This will remove the highlight over the text
  editor.setValue(userQuery, 1); // moves cursor to the end

  window.editor = editor; // Expose the editor globally if needed for resize calls
  editor.setOptions({
    enableBasicAutocompletion: true,
    enableSnippets: true,
    enableLiveAutocompletion: false, // Set to true for live autocompletion
  });
  /*
  Initial State: Both "Test" and "Hints" sections are collapsed, with the toggle indicator set to "▼".
  Interacting with Test/Hints: Clicking on either "Test" or "Hints" expands their respective content and sets the toggle indicator to "▲". It also remembers which section was last expanded.
  Using the Toggle Indicator: Clicking the toggle indicator directly will either:
  Collapse all sections if currently set to "▲", switching the indicator to "▼".
  Expand the last interacted section (or default to the first if none was interacted with yet) if currently set to "▼", switching the indicator to "▲".
  */
  let lastActiveSection = null;
  let toggleFunctionalityActivated = false;

  // console.log(document.querySelector(".container-toggle-indicator"));
  // console.log(document.querySelectorAll(".toggle"));

  const toggleIndicator = document.querySelector(".container-toggle-indicator");
  const sections = document.querySelectorAll("#test-hints-container .content");

  // Initially, ensure the toggle indicator is visible but without functionality
  toggleIndicator.style.display = "inline";
  toggleIndicator.textContent = "▼"; // Start with the indicator suggesting content is collapsed

  document.querySelectorAll(".toggle").forEach((button) => {
    button.addEventListener("click", function () {
      const targetId = this.getAttribute("data-target");
      const targetSection = document.getElementById(targetId);

      if (!toggleFunctionalityActivated) {
        // Activate toggle functionality upon first interaction
        toggleFunctionalityActivated = true;
        toggleIndicator.textContent = "▲"; // Show content is expanded
      }

      // Only the clicked section is expanded
      sections.forEach((section) => {
        if (section === targetSection) {
          section.classList.remove("collapsed");
          lastActiveSection = section; // Remember the last active section
        } else {
          section.classList.add("collapsed");
        }
      });
    });
  });

  toggleIndicator.addEventListener("click", function () {
    // Only allow toggle functionality if activated
    if (!toggleFunctionalityActivated) return;

    const isExpanded = toggleIndicator.textContent === "▲";
    toggleIndicator.textContent = isExpanded ? "▼" : "▲"; // Toggle indicator symbol

    // Expand or collapse the last active section (or all if none is specified)
    if (lastActiveSection && isExpanded) {
      lastActiveSection.classList.add("collapsed");
    } else if (lastActiveSection && !isExpanded) {
      lastActiveSection.classList.remove("collapsed");
    } else {
      // No section was previously selected; manage all sections based on the current indicator state
      sections.forEach((section) =>
        section.classList.toggle("collapsed", isExpanded)
      );
    }
  });

  // Setup toggle functionality and adjust editor height on toggle
  document
    .querySelector('.toggle[data-target="test-content"]')
    .addEventListener("click", TestQuery);

  /*
Explanation:
- requestHints Function: Sends the current SQL query and, optionally, the database schema to the backend for analysis. It then handles the response by displaying the hints or an error message.
- expandHints Function: Could request more detailed hints or further explanations based on user feedback or additional user actions. Implementation would be similar to requestHints.
- displayHints Function: A utility function to display the hints in the designated UI section. It clears the previous content and appends each hint as a new paragraph.
- Event Listeners: Set up to handle user actions, such as requesting hints or expanding on them. The visibility of the hints content is toggled when the user clicks the hints button.
*/
  // Function to request hints
  async function requestHints() {
    // const embedCode = editor.getSession().getValue();
    const userQuery = editor.getSession().getValue();
    const token = localStorage.getItem("token");

    try {
      const response = await fetch("/get-hints", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          userQuery: userQuery,
          embedCode: embedCode,
        }),
      });

      const data = await response.json();

      // console.log(data);

      if (!response.ok) throw new Error(data.error || "Failed to get hints. Need Authentication!");

      // Call displayHints only if hints are available
      if (data.hints && data.hints.length > 0) {
        displayHints(data.hints);
      } else {
        throw new Error("No hints available.");
      }
    } catch (error) {
      // Show error message and toggle visibility to ensure the user can see the error message
      document.getElementById(
        "hints-content"
      ).innerHTML = `<p class="error">${error.message}</p>`;
      document.getElementById("hints-content").classList.remove("collapsed");
    }
  }
});

async function TestQuery() {
  try {
    const sqlQuery = editor.getSession().getValue();
    // const embedCode = editor.getSession().getValue();
    // Fetch the databaseSchemaFilename from the data attribute
    const token = localStorage.getItem("token");
    const databaseSchemaFilename = document.querySelector(
      ".problem-description"
    ).dataset.databaseSchemaFilename;

    const response = await fetch("/test-sql-query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        query: sqlQuery,
        embedCode: embedCode,
        databaseSchemaFilename: databaseSchemaFilename,
      }), // Pass both the query and filename
    });
    const data = await response.json();

    // console.log(data);

    if (!response.ok) throw new Error(data.error || "Need Authentication!");
    displayTestResults(data);
  } catch (error) {
    displayTestResults({ error: error.message });
  }
}

function displayTestResults(data) {
  const resultsContainer = document.getElementById("test-results");
  resultsContainer.innerHTML = ""; // Clear previous results.

  if (data.error) {
    // Display error message.
    const errorMessage = document.createElement("p");
    errorMessage.className = "error";
    errorMessage.textContent = `Test Failed: ${data.error}`;
    resultsContainer.appendChild(errorMessage);
  } else {
    // Success message and result table.
    const errorMessage = document.createElement("p");

    errorMessage.classList.add("message"); // Add the base message class for common styling
    if (data.status === "success") {
      errorMessage.classList.add("success"); // Add the success class for color styling
      errorMessage.textContent = "Test Successful";
    } else {
      errorMessage.classList.add("message", "error-message"); // Use both classes for layout and coloring
      errorMessage.textContent = "Test Failed";
    }

    resultsContainer.appendChild(errorMessage);

    // Assuming Output and ExpectedOutput are included in the data
    if (data.status === "error") {
      const outputRows = document.createElement("p");
      outputRows.textContent = `Output Rows: ${data.Output}`;
      resultsContainer.appendChild(outputRows);

      const expectedRows = document.createElement("p");
      expectedRows.textContent = `Expected Rows: ${data.ExpectedOutput}`;
      resultsContainer.appendChild(expectedRows);
    }

    const table = document.createElement("table");
    table.className = "results-table";

    // Assuming data structure for results is an array of objects.
    const appendTable = (dataSet, title) => {
      if (dataSet && dataSet.length) {
        const tableTitle = document.createElement("h3");
        tableTitle.textContent = title;
        resultsContainer.appendChild(tableTitle);

        const table = document.createElement("table");
        table.className = "results-table";

        const thead = table.createTHead();
        const headerRow = thead.insertRow();
        Object.keys(dataSet[0]).forEach((header) => {
          const th = document.createElement("th");
          th.textContent = header;
          headerRow.appendChild(th);
        });

        const tbody = table.createTBody();
        dataSet.forEach((row) => {
          const tableRow = tbody.insertRow();
          Object.values(row).forEach((value) => {
            const cell = tableRow.insertCell();
            cell.textContent = value;
          });
        });

        resultsContainer.appendChild(table);
      } else {
        resultsContainer.textContent = "No results found.";
      }
    };

    // Append tables for userData and expectedData
    appendTable(data.userData, "Output Data");
    appendTable(data.expectedData, "Expected Data");
  }
}

/*
Explanation:
- requestHints Function: Sends the current SQL query and, optionally, the database schema to the backend for analysis. It then handles the response by displaying the hints or an error message.
- expandHints Function: Could request more detailed hints or further explanations based on user feedback or additional user actions. Implementation would be similar to requestHints.
- displayHints Function: A utility function to display the hints in the designated UI section. It clears the previous content and appends each hint as a new paragraph.
- Event Listeners: Set up to handle user actions, such as requesting hints or expanding on them. The visibility of the hints content is toggled when the user clicks the hints button.
*/
// Function to request hints
async function requestHints() {
  // const embedCode = editor.getSession().getValue();
  const userQuery = editor.getSession().getValue();
  const token = localStorage.getItem("token");

  try {
    const response = await fetch("/get-hints", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        userQuery: userQuery,
        embedCode: embedCode,
      }),
    });

    const data = await response.json();

    // console.log(data);

    if (!response.ok) throw new Error(data.error || "Failed to get hints.");

    // Call displayHints only if hints are available
    if (data.hints && data.hints.length > 0) {
      displayHints(data.hints);
    } else {
      throw new Error("No hints available.");
    }
  } catch (error) {
    // Show error message and toggle visibility to ensure the user can see the error message
    document.getElementById(
      "hints-content"
    ).innerHTML = `<p class="error">${error.message}</p>`;
    document.getElementById("hints-content").classList.remove("collapsed");
  }
}

/// Function to display hints in the UI
// Adjusted Function to Display Hints Directly from the Array Parameter
function displayHints(hintsArray) {
  const hintsContainer = document.getElementById("hints-content");
  hintsContainer.innerHTML = ""; // Clear previous hints

  if (Array.isArray(hintsArray) && hintsArray.length > 0) {
    const list = document.createElement("ul");
    hintsArray.forEach((hint) => {
      const item = document.createElement("li");
      item.textContent = hint;
      list.appendChild(item);
    });
    hintsContainer.appendChild(list);
  } else {
    hintsContainer.textContent = "No hints available.";
  }

  // Make sure hints section is visible
  hintsContainer.classList.remove("collapsed");
  hintsContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// Toggle hints section and fetch hints
document.addEventListener("click", function (e) {
  if (e.target.matches(".toggle.hints")) {
    requestHints().catch(console.error);
  }
});

// Function to expand on hints with a chain of thought
// async function expandHints() {
//     // This could be similar to requestHints but might request more detailed hints
//     // from the server or expand on the existing hints displayed to the user.
// }
