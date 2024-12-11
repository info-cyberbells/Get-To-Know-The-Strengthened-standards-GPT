const chatInput = document.querySelector('#chat-input');
const sendButton = document.querySelector('#send-btn');
const chatContainer = document.querySelector('.chat-container');
const themeBtn = document.querySelector("#theme-btn");
const deleteBtn = document.querySelector("#delete-btn");
const attachBtn = document.querySelector("#attach-btn");
const input = document.getElementById('file-upload');
const previewImg = document.getElementById('file-preview')
const previewText = document.getElementById('file-name')
const previewContainer = document.getElementById('PreviewFile')


document.addEventListener("DOMContentLoaded", function() {

}); 


attachBtn.addEventListener("click", () => {

  input.click();
})

let userText = null;

const OPENAI_API_KEY = "Enter-Your-API-KEY";
const initialHeight = chatInput.scrollHeight;


const createElement = (html, className) => {
  const chatDiv = document.createElement('div');
  chatDiv.classList.add('chat', className);
  chatDiv.innerHTML = html;

  return chatDiv;

}
const createThread = async () => {
  const APT_URL = "http://5.161.122.193:5002/api/v1/assistant/threads";
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
const previewPhoto = () => {
  const file = input.files;
  const fileName = file[0].name;
  const ext = fileName.split(".").pop().toLowerCase();
  const allowedFileTypes = ["docx", "doc"];
  let filePath = '';
  if (allowedFileTypes.includes(ext)) {
    if (file) {
      const fileReader = new FileReader();

      fileReader.onload = event => {
        if (ext == 'pdf') {
          filePath = 'assets/images/pdf.png';
        } else if (ext == 'docx' || ext == 'doc') {
          filePath = 'assets/images/docs.png';
        } else {
          filePath = event.target.result;
        }
        previewImg.setAttribute('src', filePath);
        previewText.textContent = fileName;
      }
      fileReader.readAsDataURL(file[0]);

      previewContainer.style.display = 'flex';

    }
  }
  else {
    alert("Only document files are supported");
  }

}
input.addEventListener('change', previewPhoto);


const loadDataFromLocalStorage = () => {
  // create thread


  const theme = localStorage.getItem('theme');
  const thread_id = localStorage.getItem('thread_id');

  if (!thread_id) {
    createThread();
  }

  document.body.classList.toggle("dark-mode", theme === "dark_mode");
  themeBtn.innerText = document.body.classList.contains("dark-mode") ? "light_mode" : "dark_mode";

  const defaultText = `
  <div class="default-text">
  <h1><img src="assets/images/logo.png" /></h1>
  <p>Welcome to our interactive Medical Coding and Documentation agent.</p>
  <p>How can we help you?</p>
  </div>
  `;
  chatContainer.innerHTML = localStorage.getItem('all-chats') || defaultText;
  chatContainer.scrollTo(0, chatContainer.scrollHeight);
}

loadDataFromLocalStorage();

const getChatResponse = async (incomingChatDiv) => {

  const APT_URL = "http://5.161.122.193:5002/api/v1/assistant/chat-file";
  const pElement = document.createElement('p');
  const thread_id = localStorage.getItem('thread_id');
  let content = '';

  var formData = new FormData();
  formData.append('user_query', userText);
  formData.append('thread_id', thread_id);

  // Optional: Append a file if needed
  // Example, assuming you have an input type=file with id='fileInput'
  if (input && input.files.length > 0) {
    formData.append('file', input.files[0]);
  }



  const requestOptions = {
    method: "POST",
    headers: {
      'Accept': 'text/event-stream',
    },
    body: formData
  }

  try {
    const response = await fetch(APT_URL, requestOptions);
    const reader = response.body.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('Stream complete');
        // break;
        break;
      }


      content = new TextDecoder().decode(value, { stream: true });

      incomingChatDiv.querySelector(".typing-animation")?.remove();
      // incomingChatDiv.querySelector(".chat-details").appendChild(content);


      incomingChatDiv.querySelector(".chat-details div").innerHTML += `${content}`;



      incomingChatDiv.scrollIntoView({ behavior: "smooth" });
      chatContainer.scrollTo(0, chatContainer.scrollHeight);



    }
  } catch (err) {
    pElement.textContent = "Oops something went wrong, please try again";
    pElement.classList.add('error');
    console.log(err);
  }
  // }

  // pElement.textContent = "Hi there! How can I help you today?";

  var converter = new showdown.Converter({
    omitExtraWLInCodeBlocks: true,
    simplifiedAutoLink: true,
    strikethrough: true
  });
  const convertedText = converter.makeHtml(incomingChatDiv.querySelector(".chat-details div").innerHTML);
  incomingChatDiv.querySelector(".chat-details div").innerHTML = convertedText;
  localStorage.setItem("all-chats", chatContainer.innerHTML);
}

const copyResponse = (copyBtn) => {
  const responseTextElement = copyBtn.parentElement.querySelector("div");
  // navigator.clipboard.writeText(responseTextElement.textContent);
  clipboard.writeText(responseTextElement.textContent);

  copyBtn.textContent = "done";
  setTimeout(() => copyBtn.textContent = "content_copy", 1000);
}
const showTypingAnimation = () => {
  const html = `
  <div class="chat-content">
  <div class="chat-details">
  <img src="assets/images/logo.png" alt="chatbot">
  <div markdown="1"></div>
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
  let html = `
  <div class="chat-content">
        <div class="chat-details">
         <p markdown="1"></p>
          <img src="assets/images/user.png" alt="user" />
         
        </div>
     
  `;


  if (previewImg.getAttribute('src') != "") {

    html += ` <div class="UploadedFile">
      <img src="${previewImg.getAttribute('src')}" alt="Preview Uploaded Image" />
      <div id="file-name">${previewText.innerText}</div>
    </div>`;

    previewContainer.style.display = 'none';
    previewImg.setAttribute('src', "");
    previewText.textContent = "";
  }

  html + ` </div>`;
  const outgoingChatDiv = createElement(html, 'outgoing');
  outgoingChatDiv.querySelector('p').textContent = userText;

  chatContainer.appendChild(outgoingChatDiv);
  document.querySelector(".default-text")?.remove();
  setTimeout(showTypingAnimation, 500);
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