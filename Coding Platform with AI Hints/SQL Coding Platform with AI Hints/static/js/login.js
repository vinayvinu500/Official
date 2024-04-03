function toggleForms() {
  document.getElementById("loginForm").classList.toggle("hidden");
  document.getElementById("signupForm").classList.toggle("hidden");
}

async function login() {
  const username = document.getElementById("loginUsername").value;
  const password = document.getElementById("loginPassword").value;
  if (!username || !password) {
    alert("Username and password are required.");
    return;
  }

  // Create a FormData object and append your fields to it
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  try {
    const response = await fetch("/login", {
      method: "POST",
      // Removed 'Content-Type': 'application/json' header to allow browser to set content type for FormData correctly
      body: formData, // Updated to send formData instead of JSON
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to login.");
    }

    const data = await response.json();
    localStorage.setItem("token", data.access_token); // Assuming the token key is "access_token"
    // alert("Login successful");
    window.location.href = "/question/1"; // Redirect to the home page or another page
  } catch (error) {
    alert(error.message);
  }
}


async function signup() {
  const email = document.getElementById("signupUsername").value;
  const password = document.getElementById("signupPassword").value;
  const name = email.substring(0, email.indexOf("@")); // Extract name from email

  if (!email || !password) {
    alert("Username and password are required for signup.");
    return;
  }

  try {
    const response = await fetch("/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name, email: email, password: password }), // Adjusted keys to match the backend expectations
    });

    if (!response.ok) {
      const errorResponse = await response.json();
      throw new Error(errorResponse.detail || "Failed to sign up.");
    }

    const data = await response.json();
    localStorage.setItem("token", data.access_token);
    // alert("Signup successful");
    window.location.href = "/question/1";
  } catch (error) {
    const errorResponse = await error.response.json(); // Assuming 'error' is the caught fetch error
    alert(`Error: ${errorResponse.detail}`);
  }
}

