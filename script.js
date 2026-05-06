(() => {
  const footer = document.querySelector("footer small");
  if (footer) {
    const now = new Date();
    footer.textContent += ` · Updated ${now.toLocaleDateString()}`;
  }
})();
