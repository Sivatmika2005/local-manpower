/**
 * chatbot.js - Logic for Local Service Booking Chatbot
 */
document.addEventListener('DOMContentLoaded', function() {
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotSend = document.getElementById('chatbot-send');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const typingIndicator = document.getElementById('typing-indicator');

    let isBotTyping = false;

    // Toggle Chat
    chatbotToggle.addEventListener('click', () => {
        chatbotWindow.classList.toggle('active');
        if (chatbotWindow.classList.contains('active')) {
            // If first time opening, and no messages, send greeting
            if (chatbotMessages.children.length <= 1) { // 1 because of typing indicator
                appendMessage("bot", "Hi! I can help you find services like Electrician, Plumber, or Mechanic. What do you need?");
                addQuickReplies(['Electrician', 'Plumber', 'Mechanic']);
            }
        }
    });

    chatbotClose.addEventListener('click', () => {
        chatbotWindow.classList.remove('active');
    });

    // Send Message
    chatbotSend.addEventListener('click', sendMessage);
    chatbotInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage(text = null) {
        const msgText = (text || chatbotInput.value).trim();
        if (!msgText || isBotTyping) return;

        // Add user message to UI
        appendMessage("user", msgText);
        chatbotInput.value = '';

        // Show typing indicator
        showTyping(true);

        try {
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: msgText })
            });

            const data = await response.json();
            
            // Hide typing indicator after a short delay for realism
            setTimeout(() => {
                showTyping(false);
                if (data.success) {
                    appendMessage("bot", data.reply);
                    if (data.quick_replies) {
                        addQuickReplies(data.quick_replies);
                    }
                } else {
                    appendMessage("bot", "Sorry, I'm having some trouble. Please try again later.");
                }
            }, 600);

        } catch (error) {
            console.error('Chatbot Error:', error);
            showTyping(false);
            appendMessage("bot", "Connection error. Please check if the server is running.");
        }
    }

    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;
        
        const content = document.createElement('span');
        content.textContent = text;
        msgDiv.appendChild(content);

        const time = document.createElement('span');
        time.className = 'timestamp';
        time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        msgDiv.appendChild(time);

        // Insert before typing indicator
        chatbotMessages.insertBefore(msgDiv, typingIndicator);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function addQuickReplies(replies) {
        // Remove existing ones
        const oldReplies = document.querySelector('.quick-replies');
        if (oldReplies) oldReplies.remove();

        const container = document.createElement('div');
        container.className = 'quick-replies';
        
        replies.forEach(reply => {
            const btn = document.createElement('button');
            btn.className = 'quick-reply-btn';
            btn.textContent = reply;
            btn.onclick = () => {
                if (reply === 'Clear Chat') {
                    clearChat();
                } else {
                    sendMessage(reply);
                    container.remove();
                }
            };
            container.appendChild(btn);
        });

        chatbotMessages.insertBefore(container, typingIndicator);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function showTyping(show) {
        isBotTyping = show;
        typingIndicator.style.display = show ? 'block' : 'none';
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function clearChat() {
        // Remove everything except typing indicator
        while (chatbotMessages.children.length > 1) {
            chatbotMessages.removeChild(chatbotMessages.firstChild);
        }
        // Reset session state on server
        fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ message: 'clear chat' })
        });
        appendMessage("bot", "Chat cleared. How can I help you today?");
        addQuickReplies(['Electrician', 'Plumber', 'Mechanic']);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
