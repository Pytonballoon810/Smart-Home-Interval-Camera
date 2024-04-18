let selectionBox = null;
let startX = 0;
let startY = 0;

document.addEventListener('mousedown', (event) => {
    if (event.button === 0) {
        startX = event.clientX;
        startY = event.clientY;
        selectionBox = document.createElement('div');
        selectionBox.classList.add('selection-box');
        selectionBox.style.left = `${startX}px`;
        selectionBox.style.top = `${startY}px`;
        document.body.appendChild(selectionBox);
    }
});

document.addEventListener('mousedown', (event) => {
    const items = document.querySelectorAll('.checkbox-container.selected');

    items.forEach((item) => {
        if (!item.contains(event.target)) {
            item.classList.remove('selected');
        }
    });
});

document.addEventListener('mousemove', (event) => {
    if (selectionBox !== null) {
        const currentX = event.clientX;
        const currentY = event.clientY;

        const minX = Math.min(startX, currentX);
        const minY = Math.min(startY, currentY);
        const maxX = Math.max(startX, currentX);
        const maxY = Math.max(startY, currentY);

        selectionBox.style.left = `${minX}px`;
        selectionBox.style.top = `${minY}px`;
        selectionBox.style.width = `${maxX - minX}px`;
        selectionBox.style.height = `${maxY - minY}px`;

        selectItems(minX, minY, maxX, maxY);
    }
});

document.addEventListener('mouseup', () => {
    if (selectionBox !== null) {
        document.body.removeChild(selectionBox);
        selectionBox = null;
    }
});

function selectItems(minX, minY, maxX, maxY) {
    const items = document.querySelectorAll('.checkbox-container');

    items.forEach((item) => {
        const rect = item.getBoundingClientRect();
        const itemMinX = rect.left + window.scrollX;
        const itemMinY = rect.top + window.scrollY;
        const itemMaxX = rect.right + window.scrollX;
        const itemMaxY = rect.bottom + window.scrollY;

        const isIntersecting = !(maxX < itemMinX || 
                                 maxY < itemMinY || 
                                 minX > itemMaxX || 
                                 minY > itemMaxY);

        if (isIntersecting) {
            item.querySelector('input[type="checkbox"]').checked = true;
            item.classList.add('selected');
        } else {
            item.querySelector('input[type="checkbox"]').checked = false;
            item.classList.remove('selected');
        }
    });
}
document.addEventListener('DOMContentLoaded', () => {
    const content = document.getElementById('content');

    content.addEventListener('dragover', (event) => {
        event.preventDefault();
        content.classList.add('dragover');
    });

    content.addEventListener('dragleave', () => {
        content.classList.remove('dragover');
    });

    content.addEventListener('drop', (event) => {
        event.preventDefault();
        content.classList.remove('dragover');

        const files = event.dataTransfer.files;
        const formData = new FormData();

        for (const file of files) {
            formData.append('files[]', file);
        }

        fetch('/upload_files', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

document.getElementById('backButton').addEventListener('click', () => {
    window.history.back();
});

document.getElementById('deleteButton').addEventListener('click', () => {
    const selectedFolders = Array.from(document.querySelectorAll('.folder-container input:checked'))
        .map(input => input.value);

    fetch('/delete_folders', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedFolders),
    })
    .then(response => {
        if (response.ok) {
            // Refresh the page to show the updated list of folders
            location.reload();
        } else {
            console.error('Failed to delete folders');
        }
    });
});

const contextMenu = document.getElementById('contextMenu');
const deleteOption = document.getElementById('deleteOption');
const renderOption = document.getElementById('renderOption');
let rightClickedFolder = null;

document.addEventListener('contextmenu', (event) => {
    event.preventDefault();

    // Get the folder that was right-clicked
    rightClickedFolder = event.target.closest('.folder-container');

    // Show the context menu
    contextMenu.style.display = 'block';
    contextMenu.style.left = `${event.pageX}px`;
    contextMenu.style.top = `${event.pageY}px`;
});

document.addEventListener('click', () => {
    // Hide the context menu
    contextMenu.style.display = 'none';
});

deleteOption.addEventListener('click', () => {
    // Delete the right-clicked folder or the selected folders
});

renderOption.addEventListener('click', () => {
    // Create a rendering of the right-clicked folder or the selected folders
});