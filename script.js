(() => {
  const root = document.documentElement;
  const storageKey = "theme-preference";
  const saved = localStorage.getItem(storageKey);

  if (saved === "light") {
    root.classList.add("light");
  }

  const footer = document.querySelector("footer small");
  if (footer) {
    const now = new Date();
    footer.textContent += ` · Updated ${now.toLocaleDateString()}`;
  }

  const main = document.querySelector("main");
  if (!main) {
    return;
  }

  const button = document.createElement("button");
  button.id = "theme-toggle";
  button.type = "button";
  button.style.marginTop = "1rem";
  button.style.padding = "0.5rem 0.8rem";
  button.style.borderRadius = "8px";
  button.style.border = "1px solid var(--border)";
  button.style.background = "transparent";
  button.style.color = "inherit";
  button.style.cursor = "pointer";

  const setLabel = () => {
    const isLight = root.classList.contains("light");
    button.textContent = isLight ? "Switch to dark mode" : "Switch to light mode";
    button.setAttribute("aria-pressed", String(isLight));
  };

  button.addEventListener("click", () => {
    root.classList.toggle("light");
    localStorage.setItem(storageKey, root.classList.contains("light") ? "light" : "dark");
    setLabel();
  });

  setLabel();
  main.appendChild(button);
})();
