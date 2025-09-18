// button to top created by chat GPT

document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("backToTopBtn");

  // Show button only when scrolled down 100px
  window.addEventListener("scroll", function () {
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
      btn.classList.add("show");
    } else {
      btn.classList.remove("show");
    }
  });

  // Smooth scroll back to top
  btn.addEventListener("click", function () {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  });
});
