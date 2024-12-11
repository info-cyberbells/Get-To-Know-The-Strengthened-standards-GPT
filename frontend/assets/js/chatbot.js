
// // const chatInput = document.querySelector('#chat-input');
// // const sendButton = document.querySelector('#send-btn');
// // const chatContainer = document.querySelector('.chat-container');
// // const deleteBtn = document.querySelector("#delete-btn");
// // const attachBtn = document.querySelector("#attach-btn");
// // const input = document.getElementById('file-upload');
// // const previewImg = document.getElementById('file-preview');
// // const previewText = document.getElementById('file-name');
// // const previewContainer = document.getElementById('PreviewFile');

// // const API_BASE_URL = "http://127.0.0.1:8000";
// // let userText = null;

// // // Format reference
// // const formatReference = (text) => {
// //     return text.replace(/【\d+:\d+†([^】]+)】/g, (match, filename) => {
// //         return `<span class="reference-citation">${filename}</span>`;
// //     });
// // };

// // // Initialize chat interface
// // const initializeChat = async () => {
// //     loadDataFromLocalStorage();
// //     adjustTextareaHeight();
// //     await checkServerConnection();
// // };

// // // Check server connection
// // const checkServerConnection = async () => {
// //     try {
// //         const response = await fetch(`${API_BASE_URL}/api/v1/assistant/health`);
// //         if (!response.ok) throw new Error('Server connection failed');
// //         return true;
// //     } catch (error) {
// //         console.error('Server connection error:', error);
// //         showError('Unable to connect to server. Please try again later.');
// //         return false;
// //     }
// // };

// // // Create chat thread
// // const createThread = async () => {
// //     try {
// //         const response = await fetch(`${API_BASE_URL}/api/v1/assistant/threads`, {
// //             method: "GET",
// //             headers: {
// //                 "Content-Type": "application/json",
// //                 'Access-Control-Allow-Origin': '*'
// //             }
// //         });
        
// //         if (!response.ok) throw new Error('Failed to create thread');
        
// //         const data = await response.json();
// //         localStorage.setItem('thread_id', data.data.id);
// //         return data.data.id;
// //     } catch (error) {
// //         console.error('Thread creation error:', error);
// //         showError('Failed to initialize chat. Please refresh the page.');
// //         return null;
// //     }
// // };

// // // Handle file preview
// // const previewPhoto = () => {
// //     const file = input.files[0];
// //     if (!file) return;

// //     const fileName = file.name;
// //     const ext = fileName.split(".").pop().toLowerCase();
// //     const allowedFileTypes = ["docx", "doc", "pdf"];
    
// //     if (!allowedFileTypes.includes(ext)) {
// //         showError("Only document files (.doc, .docx, .pdf) are supported");
// //         input.value = '';
// //         return;
// //     }

// //     const filePath = ext === 'pdf' ? 'assets/images/pdf.png' : 'assets/images/docs.png';
// //     previewImg.src = filePath;
// //     previewText.textContent = fileName;
// //     previewContainer.style.display = 'flex';
// // };

// // // Load chat data from localStorage
// // const loadDataFromLocalStorage = () => {
// //     const thread_id = localStorage.getItem('thread_id');

// //     if (!thread_id) {
// //         createThread();
// //     }

// //     const defaultText = `
// //         <div class="default-text">
// //             <p>Welcome to our interactive Get To Know The Strengthened Standards agent.</p>
// //             <p>How can I assist you today?</p>
// //         </div>
// //     `;
// //     chatContainer.innerHTML = localStorage.getItem('all-chats') || defaultText;
// //     chatContainer.scrollTo(0, chatContainer.scrollHeight);
// // };

// // // Show error message
// // const showError = (message) => {
// //     const errorDiv = document.createElement('div');
// //     errorDiv.className = 'error-message';
// //     errorDiv.style.cssText = `
// //         color: #721c24;
// //         background-color: #f8d7da;
// //         border: 1px solid #f5c6cb;
// //         padding: 10px;
// //         margin: 10px 0;
// //         border-radius: 4px;
// //         text-align: center;
// //     `;
// //     errorDiv.textContent = message;
// //     chatContainer.appendChild(errorDiv);
// //     chatContainer.scrollTo(0, chatContainer.scrollHeight);
// //     setTimeout(() => errorDiv.remove(), 5000);
// // };

// // // Create chat elements
// // const createElement = (html, className) => {
// //     const chatDiv = document.createElement('div');
// //     chatDiv.classList.add('chat', className);
// //     chatDiv.innerHTML = html;
// //     return chatDiv;
// // };

// // // Process markdown chunks
// // const processMarkdownChunk = (text, buffer) => {
// //     const fullText = buffer + text;
    
// //     const lastHash = fullText.lastIndexOf('#');
// //     const lastAsterisk = fullText.lastIndexOf('*');
// //     const lastUnderscore = fullText.lastIndexOf('_');
// //     const lastBacktick = fullText.lastIndexOf('`');
    
// //     const markers = [lastHash, lastAsterisk, lastUnderscore, lastBacktick]
// //         .filter(pos => pos !== -1);
    
// //     if (markers.length === 0) {
// //         return { 
// //             complete: fullText,
// //             remaining: ''
// //         };
// //     }
    
// //     const lastMarker = Math.max(...markers);
// //     const nextNewline = fullText.indexOf('\n', lastMarker);
    
// //     if (nextNewline !== -1) {
// //         return {
// //             complete: fullText.substring(0, nextNewline),
// //             remaining: fullText.substring(nextNewline)
// //         };
// //     }
    
// //     return {
// //         complete: fullText.substring(0, lastMarker),
// //         remaining: fullText.substring(lastMarker)
// //     };
// // };

// // // Get chat response from API
// // const getChatResponse = async (incomingChatDiv) => {
// //     const thread_id = localStorage.getItem('thread_id');
// //     if (!thread_id) {
// //         showError('Chat session not initialized. Please refresh the page.');
// //         return;
// //     }

// //     const formData = new FormData();
// //     formData.append('user_query', userText);
// //     formData.append('thread_id', thread_id);

// //     if (input.files.length > 0) {
// //         formData.append('file', input.files[0]);
// //     }

// //     try {
// //         const response = await fetch(`${API_BASE_URL}/api/v1/assistant/chat-file`, {
// //             method: "POST",
// //             headers: {
// //                 'Accept': 'text/event-stream',
// //             },
// //             body: formData
// //         });

// //         if (!response.ok) {
// //             const errorData = await response.json();
// //             throw new Error(errorData.detail || 'Failed to process request');
// //         }

// //         const converter = new showdown.Converter({
// //             omitExtraWLInCodeBlocks: true,
// //             simplifiedAutoLink: true,
// //             strikethrough: true,
// //             parseImgDimensions: true,
// //             simpleLineBreaks: true,
// //             tables: true,
// //             tasklists: true,
// //             ghCodeBlocks: true,
// //             requireSpaceBeforeHeadingText: true,
// //             emoji: true
// //         });

// //         const reader = response.body.getReader();
// //         const textDecoder = new TextDecoder();
// //         let buffer = '';
// //         let accumulatedContent = '';
        
// //         while (true) {
// //             const { done, value } = await reader.read();
// //             if (done) break;

// //             const chunk = textDecoder.decode(value, { stream: true });
// //             const { complete, remaining } = processMarkdownChunk(chunk, buffer);
// //             buffer = remaining;
            
// //             if (complete) {
// //                 accumulatedContent += complete;
// //                 let html = converter.makeHtml(accumulatedContent);
// //                 html = formatReference(html);
                
// //                 incomingChatDiv.querySelector(".typing-animation")?.remove();
// //                 const messageContent = incomingChatDiv.querySelector(".chat-details div");
// //                 messageContent.innerHTML = html;
                
// //                 incomingChatDiv.scrollIntoView({ behavior: "smooth" });
// //                 chatContainer.scrollTo(0, chatContainer.scrollHeight);
// //             }
// //         }

// //         if (buffer) {
// //             accumulatedContent += buffer;
// //             let html = converter.makeHtml(accumulatedContent);
// //             html = formatReference(html);
// //             const messageContent = incomingChatDiv.querySelector(".chat-details div");
// //             messageContent.innerHTML = html;
// //         }
        
// //         localStorage.setItem("all-chats", chatContainer.innerHTML);

// //     } catch (error) {
// //         console.error('API response error:', error);
// //         if (error.response) {
// //             console.error('Response status:', error.response.status);
// //             console.error('Response data:', error.response.data);
// //         }
// //         throw error;
// //         // if (incomingChatDiv) {
// //         //     const messageContent = incomingChatDiv.querySelector(".chat-details div");
// //         //     if (messageContent) {
// //         //         messageContent.innerHTML = `<div class="error-message">${errorMessage}</div>`;
// //         //     }
// //         // }
// //     }
// // };

// // // Show typing animation
// // const showTypingAnimation = () => {
// //     const html = `
// //         <div class="chat-content">
// //             <div class="chat-details">
// //                 <div markdown="1"></div>
// //                 <div class="typing-animation">
// //                     <div class="typing-dot" style="--delay: 0.2s"></div>
// //                     <div class="typing-dot" style="--delay: 0.3s"></div>
// //                     <div class="typing-dot" style="--delay: 0.4s"></div>
// //                 </div>
// //             </div>
// //         </div>
// //     `;

// //     const incomingChatDiv = createElement(html, 'incoming');
// //     chatContainer.appendChild(incomingChatDiv);
// //     chatContainer.scrollTo(0, chatContainer.scrollHeight);
// //     getChatResponse(incomingChatDiv);
// // };

// // // Handle outgoing chat
// // const handleOutgoingChat = async (e) => { 
// //     if (e) e.preventDefault();  // Prevent any default form submission
// //     userText = chatInput.value.trim();
// //     if (!userText) return;

// //     //window.location.reload = function() {};
// //     //window.location.href = window.location.href;

// //     const hasFile = input.files.length > 0;
// //     console.log('Has file:', hasFile);  // Debug log
    
// //     const currentPreviewSrc = previewImg.src;
// //     // console.log(currentPreviewSrc)
// //     const currentFileName = previewText.textContent;
// //     // console.log(currentFileName)

// //     let html = `
// //         <div class="chat-content">
// //             <div class="chat-details">
// //                 <img src="assets/images/user.png" alt="user">
// //                 <p markdown="1">${userText}</p>
// //             </div>
// //     `;

// //     if (currentPreviewSrc) {
// //         html += `
// //             <div class="file-preview">
// //                 <img src="${currentPreviewSrc}" alt="Preview Uploaded Image">
// //                 <div class="file-name">${currentFileName}</div>
// //             </div>
// //         `;
// //     }

// //     html += `</div>`;
// //     console.log(currentPreviewSrc)
    
// //     const outgoingChatDiv = createElement(html, 'outgoing');
// //     console.log(outgoingChatDiv)

// //     chatContainer.appendChild(outgoingChatDiv);
// //     console.log(outgoingChatDiv)
   
// //     document.querySelector(".default-text")?.remove();
  
    
// //     chatInput.value = '';
// //     adjustTextareaHeight();

// //     // Show typing animation first
// //     showTypingAnimation();
// //     // return false;
// //     // Clear preview only after successful processing
// //     if (hasFile) {
// //         try {
// //             console.log('Processing file...');  // Debug log
// //             setTimeout(() => {
// //                 previewContainer.style.display = 'none';
// //                 previewImg.src = "";
// //                 previewText.textContent = "";
// //                 input.value = '';
// //             }, 4000);
// //         } catch (error) {
// //             console.error('File processing error:', error);
// //             showError('Error processing file');
// //         }
// //     }
    
// //     return false;  // Prevent form submission

// // };
// // // Prevent form submissions
// // document.addEventListener('submit', (e) => {
// //     e.preventDefault();
// //     return false;
// // });
// // // Adjust textarea height
// // const adjustTextareaHeight = () => {
// //     chatInput.style.height = 'auto';
// //     chatInput.style.height = chatInput.scrollHeight + 'px';
// // };

// // // Event Listeners
// // input.addEventListener('change', previewPhoto);
// // // attachBtn.addEventListener("click", () => input.click());

// // attachBtn.addEventListener("click", (e) => {
// //     e.preventDefault();
// //     input.click();
// // });

// // deleteBtn.addEventListener("click", () => {
// //     if (confirm("Are you sure you want to delete all chats?")) {
// //         localStorage.removeItem("all-chats");
// //         localStorage.removeItem("thread_id");
// //         chatContainer.innerHTML = `
// //             <div class="default-text">
// //                 <p>Welcome to our interactive Get To Know The Strengthened Standards agent.</p>
// //                 <p>How can I assist you today?</p>
// //             </div>
// //         `;
// //         createThread();
// //     }
// // });

// // chatInput.addEventListener('input', adjustTextareaHeight);

// // chatInput.addEventListener('keydown', (e) => {
// //     if (e.key === 'Enter' && !e.shiftKey && window.innerWidth > 800) {
// //         e.preventDefault();
// //         handleOutgoingChat();
// //     }
// // });

// // sendButton.addEventListener('click', handleOutgoingChat);
// // sendButton.addEventListener('click', (e) => {
// //     e.preventDefault();  // Prevent form submission
// //     console.log('Send button clicked');
// //     handleOutgoingChat();
// // });
// // // Initialize the chat
// // initializeChat();



const chatInput = document.querySelector('#chat-input');
const sendButton = document.querySelector('#send-btn');
const chatContainer = document.querySelector('.chat-container');
const themeBtn = document.querySelector("#theme-btn");
const deleteBtn = document.querySelector("#delete-btn");
const attachBtn = document.querySelector("#attach-btn");
const input = document.getElementById('file-upload');

const fakeContent = {
  "Pick info from the file": `Ananlye all text content, response from file with propery query answer.`
}

const API_BASE_URL = "http://127.0.0.1:5002";  // enter here your server ip

// Convert markdown to HTML
const markdownToHtml = (text) => {
  // Handle bullet points first
  text = text.replace(/^\s*[\*\-]\s+(.+)/gm, '<li>$1</li>');
  text = text.replace(/(<li>.*?<\/li>)\n*/gs, '<ul>$1</ul>');
  
  // Convert bold text
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Convert newlines to paragraphs (excluding lists)
  const paragraphs = text.split('\n\n');
  text = paragraphs.map(para => {
    if (!para.includes('<ul>')) {
      return `<p>${para.trim()}</p>`;
    }
    return para;
  }).join('');
  
  return text;
}

attachBtn.addEventListener("click", () => {
  input.click();
});

let userText = null;
const OPENAI_API_KEY = "";
const initialHeight = chatInput.scrollHeight;

const createElement = (html, className) => {
  const chatDiv = document.createElement('div');
  chatDiv.classList.add('chat', className);
  chatDiv.innerHTML = html;
  return chatDiv;
}

const createThread = async () => {
  const APT_URL = "{API_BASE_URL}/api/v1/assistant/threads";    
  const requestOptions = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      'Access-Control-Allow-Origin': '*'
    }
  }

  try {
    const response = await (await fetch(APT_URL, requestOptions)).json();
    console.log(response);
    localStorage.setItem('thread_id', response.data.id);
  } catch (err) {
    console.log(err);
  }
}

const previewFile = () => {
  const file = input.files[0];
  const fileName = document.getElementById('file-name');
  
  if (file) {
    fileName.textContent = file.name;
    
    if (file.type.startsWith('image/')) {
      const preview = document.getElementById('file-preview');
      const fileReader = new FileReader();
      fileReader.onload = (event) => {
        preview.setAttribute('src', event.target.result);
        preview.style.display = 'block';
      };
      fileReader.readAsDataURL(file);
    } else {
      document.getElementById('file-preview').style.display = 'none';
    }
    
    document.getElementById('PreviewFile').style.display = 'flex';
  } else {
    document.getElementById('PreviewFile').style.display = 'none';
    fileName.textContent = '';
  }
};

input.addEventListener('change', previewFile);

const loadDataFromLocalStorage = () => {
  const theme = localStorage.getItem('theme');
  const thread_id = localStorage.getItem('thread_id');

  if (!thread_id) {
    createThread();
  }

  document.body.classList.toggle("dark-mode", theme === "dark_mode");
  themeBtn.innerText = document.body.classList.contains("dark-mode") ? "light_mode" : "dark_mode";

  const defaultText = `
  <div class="default-text">
            <p>Welcome to our interactive Get To Know The Strengthened Standards agent.</p>
            <p>How can I assist you today?</p>
        </div>
  `;
  chatContainer.innerHTML = localStorage.getItem('all-chats') || defaultText;
  chatContainer.scrollTo(0, chatContainer.scrollHeight);
}

loadDataFromLocalStorage();

const getChatResponse = async (incomingChatDiv, input) => {
  const APT_URL = "{API_BASE_URL}/api/v1/assistant/chat-file";   //enter your server base url
  const pElement = document.createElement('p');
  const thread_id = localStorage.getItem('thread_id');

  const formData = new FormData();
  formData.append('user_query', userText);
  formData.append('thread_id', thread_id);

  if (input && input.files.length > 0) {
    const file = input.files[0];
    formData.append('file', file);
    console.log("File details:", file);
  } else {
    console.log("No file selected.");
  }

  const requestOptions = {
    method: "POST",
    body: formData
  };

  try {
    const response = await fetch(APT_URL, requestOptions);
    const content = await response.text();
    console.log('Response received:', content);

    incomingChatDiv.querySelector(".typing-animation")?.remove();
    
    // Convert markdown to HTML and set content
    const formattedContent = markdownToHtml(content);
    const chatDetailsP = incomingChatDiv.querySelector(".chat-details p");
    chatDetailsP.innerHTML = formattedContent;
    
    // Add custom styles to the chat content
    chatDetailsP.style.fontSize = '16px';
    chatDetailsP.style.lineHeight = '1.6';
    
    incomingChatDiv.scrollIntoView({ behavior: "smooth" });
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    const preview = document.getElementById('file-preview');
    preview.style.display = 'none';
    input.value = '';
  } catch (err) {
    pElement.textContent = "Oops something went wrong, please try again";
    pElement.classList.add('error');
    console.log(err);
  }

  localStorage.setItem("all-chats", chatContainer.innerHTML);
};

const copyResponse = (copyBtn) => {
  const responseTextElement = copyBtn.parentElement.querySelector("p");
  navigator.clipboard.writeText(responseTextElement.textContent);
  copyBtn.textContent = "done";
  setTimeout(() => copyBtn.textContent = "content_copy", 1000);
}

const showTypingAnimation = () => {
  const html = `
  <div class="chat-content">
    <div class="chat-details">
      <img src="assets/images/logo.png" alt="chatbot">
      <p class="response-text"></p>
      <div class="typing-animation">
        <div class="typing-dot" style="--delay: 0.2s"></div>
        <div class="typing-dot" style="--delay: 0.3s"></div>
        <div class="typing-dot" style="--delay: 0.4s"></div>
      </div>
    </div>
    <span onClick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
  </div>
  `;

  const incomingChatDiv = createElement(html, 'incoming');
  chatContainer.appendChild(incomingChatDiv);
  chatContainer.scrollTo(0, chatContainer.scrollHeight);
  getChatResponse(incomingChatDiv);
}

const handleOutgoingChat = () => {
  userText = chatInput.value.trim();
  if (!userText) return;
  
  const html = `
  <div class="chat-content">
    <div class="chat-details">
      <p></p>
      <img src="assets/images/user.png" alt="user" />
    </div>
  </div>
  `;

  const outgoingChatDiv = createElement(html, 'outgoing');
  outgoingChatDiv.querySelector('p').textContent = userText;
  chatContainer.appendChild(outgoingChatDiv);
  document.querySelector(".default-text")?.remove();
  
  setTimeout(() => {
    showTypingAnimation();
    document.getElementById('PreviewFile').style.display = 'none';
    document.getElementById('file-name').textContent = '';
    input.value = '';
  }, 500);
  
  chatInput.value = '';
  chatContainer.scrollTo(0, chatContainer.scrollHeight);
};

themeBtn.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
  localStorage.setItem("theme", themeBtn.innerText);
  themeBtn.innerText = document.body.classList.contains("dark-mode") ? "light_mode" : "dark_mode";
});

deleteBtn.addEventListener("click", () => {
  if (confirm("Are you sure you want to delete all chats?")) {
    localStorage.removeItem("all-chats");
    localStorage.removeItem("thread_id");
    loadDataFromLocalStorage();
  }
});

chatInput.addEventListener('input', () => {
  chatInput.style.height = initialHeight + 'px';
  chatInput.style.height = chatInput.scrollHeight + 'px';
});

chatInput.addEventListener('keydown', (e) => {
  if (e.keyCode === 13 && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleOutgoingChat();
  }
});

sendButton.addEventListener('click', handleOutgoingChat);