export function registerServiceWorker() {
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("/sw.js")
        .then((registration) => {
          console.info("[sw] registered", registration.scope);
        })
        .catch((error) => {
          console.error("[sw] registration failed", error);
        });
    });
  }
}
