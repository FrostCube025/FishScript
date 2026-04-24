const copyBtn = document.getElementById("copyBtn");
const exampleCode = document.getElementById("exampleCode");

copyBtn.addEventListener("click", async () => {
  await navigator.clipboard.writeText(exampleCode.innerText);
  copyBtn.innerText = "Copied!";
  setTimeout(() => {
    copyBtn.innerText = "Copy example";
  }, 1200);
});
