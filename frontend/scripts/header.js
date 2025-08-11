// Wait for header to load
document.addEventListener("click", function(e) {
  if (e.target.id === "openModalBtn") {
    document.getElementById("locationModal").style.display = "block";
  }
  if (e.target.id === "signinBtn") {
    document.getElementById("signinModal").style.display = "block";
  }
  if (e.target.classList.contains("close")) {
    document.getElementById("locationModal").style.display = "none";
  }
  if (e.target.classList.contains("closeSignin")) {
    document.getElementById("signinModal").style.display = "none";
  }
});

window.onclick = function(event) {
  if (event.target.classList.contains("modal")) {
    event.target.style.display = "none";
  }
};
