// Get the grid container
const gridContainer = document.getElementById("clients");

fetch("/api/get-clients")
  .then((response) => response.json())
  .then((clients) => {
    // Do something with the clients
    console.log(clients);

    // Loop over the data
    for (const item of clients) {
      // Create a new div for each item
      const gridItem = document.createElement("div");
      const span = document.createElement("span");
      const img = document.createElement("img");
      span.innerText = item;
      img.src = `/icons/folder.png`;
      gridItem.appendChild(span);
      gridItem.appendChild(img);

      // Add the item to the grid container
      gridContainer.appendChild(gridItem);
    }
  })
  .catch((error) => console.error("Error:", error));
