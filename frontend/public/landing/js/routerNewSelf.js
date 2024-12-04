function GotoNewLink(newLink) {
    window.parent.postMessage({ action: "navigate", path: `/${newLink}`}, "*");
}