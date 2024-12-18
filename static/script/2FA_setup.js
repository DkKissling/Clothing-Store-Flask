document.getElementById("method").addEventListener("change", function() {
  const method = this.value;
  document.getElementById("smsField").style.display = "none";
  document.getElementById("emailField").style.display = "none";

  if (method === "sms") {
      document.getElementById("smsField").style.display = "block";
  } else if (method === "email") {
      document.getElementById("emailField").style.display = "block";
  }
});

document.getElementById("auth-setup-form").addEventListener("submit", function(event) {
  event.preventDefault();

  document.getElementById("verificationSection").style.display = "block";
});

document.getElementById("verifyButton").addEventListener("click", function() {
  const code = document.getElementById("verificationCode").value;

  if (code === "123456") {
      document.getElementById("successMsg").style.display = "block";
      document.getElementById("errorMsg").style.display = "none";
  } else {
      document.getElementById("errorMsg").style.display = "block";
      document.getElementById("successMsg").style.display = "none";
  }
});