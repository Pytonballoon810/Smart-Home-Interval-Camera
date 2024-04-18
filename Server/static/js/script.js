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
      gridItem.textContent = item;

      // Add the item to the grid container
      gridContainer.appendChild(gridItem);
    }
  })
  .catch((error) => console.error("Error:", error));
