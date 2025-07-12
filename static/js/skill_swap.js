// Select the buttons
const likeBtn = document.querySelector('.like-btn-custom');
const commentBtn = document.querySelector('.comment-btn');
const shareBtn = document.querySelector('.share-btn');
const joinBtn = document.querySelector('.join-btn');
const commentSection = document.querySelector('.comment-section'); // Select the comment box section



// Like button toggle functionality
document.querySelectorAll('.like-btn').forEach((likeBtn) => {
    let isClicked = false;
    likeBtn.addEventListener('click', () => {
        if (isClicked) {
            likeBtn.style.background = ''; // Reset the background
            likeBtn.style.color = ''; // Reset the text color
            likeBtn.style.transform = 'scale(1.0)';
            isClicked = false;
        } else {
            likeBtn.style.background = 'linear-gradient(135deg,rgb(0, 84, 84),rgb(0, 129, 129))';
            likeBtn.style.color = 'white';
            likeBtn.style.transform = 'scale(1.10)';
            isClicked = true;
        }
    });
});

// Comment button toggle functionality
document.querySelectorAll('.comment-btn').forEach((button, index) => {
    button.addEventListener('click', () => {
        const commentSection = document.querySelectorAll('.comment-section')[index];
        if (commentSection.style.display === 'block') {
            commentSection.style.display = 'none';
        } else {
            commentSection.style.display = 'block';
            commentSection.querySelector('.comment-box').focus();
        }
    });
});

// Handling comment submission and clearing comment box
document.querySelectorAll('.comment-box').forEach((commentBox) => {
    commentBox.addEventListener('keypress', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();

            const messageDiv = document.createElement('div');
            messageDiv.textContent = "Comment Posted.! 🎉";
            messageDiv.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background-color: #ffffff;
                padding: 20px 40px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                font-size: 18px;
                font-weight: bold;
                z-index: 1;
            `;

            document.body.appendChild(messageDiv);
            commentBox.value = '';

            setTimeout(() => {
                messageDiv.remove();
            }, 1000);
        }
    });
});

// Share button functionality
document.querySelectorAll('.share-btn').forEach((shareBtn) => {
    shareBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('Link copied!');
        }).catch((err) => {
            console.error('Failed to copy: ', err);
        });
    });
});

// Join Project button functionality
document.querySelectorAll('.join-btn').forEach((joinBtn) => {
    joinBtn.addEventListener('click', () => {
        joinBtn.classList.toggle('clicked');
        joinBtn.textContent = joinBtn.classList.contains('clicked') ? 'View Project' : 'Request Sent.!';
    });
});

// Follow button toggle
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".follow-btn").forEach(followButton => {
        followButton.addEventListener("click", function() {
            if (followButton.classList.contains("following")) {
                followButton.classList.remove("following");
                followButton.innerHTML = "Follow +👤";
                followButton.style.backgroundColor = "#0073b1";
            } else {
                followButton.classList.add("following");
                followButton.innerHTML = "Following ✅";
                followButton.style.backgroundColor = "#28a745";
            }
        });
    });

    document.querySelectorAll(".message-btn").forEach(button => {
        button.addEventListener("click", () => {
            const modalId = button.getAttribute("data-modal");
            document.getElementById(modalId).style.display = "block";
        });
    });

    document.querySelectorAll(".close-btn").forEach(button => {
        button.addEventListener("click", () => {
            const modalId = button.getAttribute("data-modal");
            document.getElementById(modalId).style.display = "none";
        });
    });

    document.querySelectorAll(".sendMessageBtn").forEach(button => {
        button.addEventListener("click", () => {
            const inputId = button.getAttribute("data-input");
            const messageInput = document.getElementById(inputId);
            const message = messageInput.value.trim();
            if (message !== "") {
                alert("Message sent: " + message);
                button.closest(".modal").style.display = "none";
            } else {
                alert("Please enter a message.");
            }
        });
    });

    window.addEventListener("click", (event) => {
        document.querySelectorAll(".modal").forEach(modal => {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    });
});

function toggleJoinText(button) {
    button.innerText = 'View Project';
    button.classList.add('clicked');
}

// Ensure dropdown menu toggle works
document.getElementById('emailDropdown').addEventListener('click', function (e) {
    var dropdownMenu = e.target.nextElementSibling;
    dropdownMenu.classList.toggle('show');
});
