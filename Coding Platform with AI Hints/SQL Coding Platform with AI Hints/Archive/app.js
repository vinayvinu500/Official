var csrftoken = getCookie("csrftoken");

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Function to get the current time of day
function getTimeOfDay() {
  var now = new Date();
  var hours = now.getHours();

  if (hours >= 5 && hours < 12) {
    return "Good morning, ready for some Python?";
  } else if (hours >= 12 && hours < 18) {
    return "Good afternoon, ready for some Python?";
  } else {
    return "Good evening , ready for some Python?";
  }
}

// Set the salutation based on the time of day
var salutation = getTimeOfDay();
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("salutation").innerText = salutation;
});
