document.addEventListener("DOMContentLoaded", function () {
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        obs.unobserve(img); // stop observing once loaded
      }
    });
  }, {
    rootMargin: "100px", // preloads slightly before it scrolls into view
    threshold: 0.01
  });

  document.querySelectorAll('img.lazy-svg').forEach(img => {
    observer.observe(img);
  });
});