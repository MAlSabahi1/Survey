console.log("custom.js loaded");

// Check if Bootstrap is loaded
if (typeof bootstrap === "undefined") {
    console.log("Bootstrap JS is not loaded. Please check the path or file.");
} else {
    console.log("Bootstrap JS is loaded.");
}

// Function to set the form action dynamically for deletion
function setDeleteAction(surveyId) {
    console.log("Setting delete action for survey:", surveyId); // Debugging log
    const deleteForm = document.getElementById('deleteForm');
    deleteForm.action = `/survey/${surveyId}/delete/`;
}

// Ensure this function is available globally
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed"); // Debugging log

    const deleteButtons = document.querySelectorAll(".delete-button");

    deleteButtons.forEach(button => {
        button.addEventListener("click", function () {
            const surveyId = button.getAttribute("data-survey-id");
            console.log("Delete button clicked for survey:", surveyId); // Debugging log
            setDeleteAction(surveyId);
        });
    });
});



