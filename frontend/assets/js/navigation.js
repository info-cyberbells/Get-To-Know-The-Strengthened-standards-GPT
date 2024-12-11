class Navigation {
    constructor() {
        this.init();
    }

    init() {
        this.createNavBar();
        this.createFooter();
        this.createLoginOverlay();
        this.setActivePage();
        this.initTheme();
        this.checkAuthentication();
        this.initializeEventListeners();
        this.createHelpOverlay(); // Create help overlay last to avoid interference
    }

    createNavBar() {
        // Remove existing navigation if present
        const existingNav = document.querySelector('.nav-banner');
        if (existingNav) {
            existingNav.remove();
        }

        const header = document.createElement('div');
        header.className = 'header nav-banner';
        header.innerHTML = `
            <div class="nav-left">
                <img src="assets/images/MCCSA-horizontal strapline 72dpi.png" alt="MCCSA Logo" class="nav-logo" style="cursor: pointer;">
            </div>
            <div class="nav-links">
                <a href="guidance.html" class="nav-button">Guidance</a>
                <a href="index.html" class="nav-button">Chatbot</a>
                <a href="promptgallery.html" class="nav-button">Prompt Gallery</a>
                <button id="signout-btn" class="nav-button">Sign Out</button>
            </div>
            <div class="nav-right">
                <span id="theme-btn" class="material-symbols-rounded theme-toggle">dark_mode</span>
                <span id="help-btn" class="material-symbols-rounded">help</span>
            </div>
        `;

        // Insert at the very beginning of the body
        document.body.insertBefore(header, document.body.firstChild);

        // Logo click handler
        const logo = header.querySelector('.nav-logo');
        logo.addEventListener('click', () => {
            window.location.href = 'guidance.html';
        });

        // Navigation links click handlers
        const navLinks = document.querySelectorAll('.nav-button:not(#signout-btn)');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const href = link.getAttribute('href');
                window.location.href = href;
            });
        });

        // Sign out button handler
        const signoutBtn = header.querySelector('#signout-btn');
        signoutBtn.addEventListener('click', () => {
            localStorage.removeItem('isAuthenticated');
            window.location.reload();
        });
    }

    createHelpOverlay() {
        // Remove existing help overlay if present
        const existingHelpOverlay = document.getElementById('helpOverlay');
        if (existingHelpOverlay) {
            existingHelpOverlay.remove();
        }

        const helpOverlay = document.createElement('div');
        helpOverlay.id = 'helpOverlay';
        helpOverlay.className = 'help-overlay';
        helpOverlay.innerHTML = `
            <div class="help-box">
                <button class="close-help material-symbols-rounded">close</button>
                <h2>Need Help?</h2>
                <p>If you encounter any issues or need assistance, please contact our support team at:</p>
                <p><a href="mailto:george.gouzounis@mccsa.org.au">george.gouzounis@mccsa.org.au</a></p>
            </div>
        `;

        document.body.appendChild(helpOverlay);

        // Close button handler
        const closeBtn = helpOverlay.querySelector('.close-help');
        closeBtn.addEventListener('click', () => {
            helpOverlay.classList.remove('visible');
        });

        // Close on overlay click
        helpOverlay.addEventListener('click', (e) => {
            if (e.target === helpOverlay) {
                helpOverlay.classList.remove('visible');
            }
        });

        // Help button handler
        const helpBtn = document.querySelector('#help-btn');
        if (helpBtn) {
            helpBtn.addEventListener('click', () => {
                helpOverlay.classList.add('visible');
            });
        }
    }

    createLoginOverlay() {
        // Remove existing overlay if present
        const existingOverlay = document.getElementById('loginOverlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }

        const loginOverlay = document.createElement('div');
        loginOverlay.id = 'loginOverlay';
        loginOverlay.className = 'login-overlay';
        loginOverlay.innerHTML = `
            <div class="login-container">
                <h2 style="margin-bottom: 1.5rem; color: var(--text-color);">Login Required</h2>
                <input type="password" id="txtPassword" placeholder="Enter Password">
                <div id="loginError" style="color: red; margin-top: 10px; display: none;">Incorrect password. Please try again.</div>
                <button class="login-btn" onclick="navigation.validatePassword()">Login</button>
            </div>
        `;

        document.body.appendChild(loginOverlay);
    }

    createFooter() {
        // Remove existing footer if present
        const existingFooter = document.querySelector('.site-footer');
        if (existingFooter) {
            existingFooter.remove();
        }

        const footer = document.createElement('footer');
        footer.className = 'site-footer';
        footer.innerHTML = `
            <div class="footer-content">
                <div class="footer-left">
                    <p>Get To Know The Strengthened Standards GPT - 2025</p>
                </div>
                <div class="footer-center">
                    <div class="standards-link-container">
                        <a href="https://www.agedcarequality.gov.au/providers/quality-standards/strengthened-quality-standards" 
                           target="_blank" 
                           rel="noopener noreferrer"
                           class="standards-link">
                           Visit Strengthened Quality Standards Website
                        </a>
                    </div>
                </div>
                <div class="footer-right">
                    <p>E: <a href="mailto:george.gouzounis@mccsa.org.au" class="footer-email">george.gouzounis@mccsa.org.au</a></p>
                </div>
            </div>
        `;

        document.body.appendChild(footer);
    }

    setActivePage() {
        const currentPath = window.location.pathname;
        const currentPage = currentPath.split('/').pop() || 'index.html';
        const navButtons = document.querySelectorAll('.nav-button:not(#signout-btn)');
        
        navButtons.forEach(button => {
            const linkPath = button.getAttribute('href');
            if (linkPath === currentPage || 
                (currentPage === '' && linkPath === 'index.html') ||
                (currentPage === '/' && linkPath === 'index.html')) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }

    initTheme() {
        const themeBtn = document.querySelector("#theme-btn");
        
        const loadTheme = () => {
            const theme = localStorage.getItem('theme');
            document.body.classList.toggle("dark-mode", theme === "dark_mode");
            themeBtn.innerText = document.body.classList.contains("dark-mode") ? "light_mode" : "dark_mode";
        };

        themeBtn.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            localStorage.setItem("theme", themeBtn.innerText);
            themeBtn.innerText = document.body.classList.contains("dark-mode") ? "light_mode" : "dark_mode";
        });

        loadTheme();
    }

    validatePassword() {
        const password = document.getElementById("txtPassword").value;
        const errorElement = document.getElementById("loginError");
        
        if (password !== 'agedMCCSA83!') {
            errorElement.style.display = 'block';
            return false;
        }
        
        errorElement.style.display = 'none';
        localStorage.setItem('isAuthenticated', 'true');
        document.getElementById("loginOverlay").style.display = "none";
        document.getElementById("contentContainer").classList.add('visible');
    }

    checkAuthentication() {
        const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
        const loginOverlay = document.getElementById('loginOverlay');
        const contentContainer = document.getElementById('contentContainer');
        
        if (!isAuthenticated) {
            if (loginOverlay) {
                loginOverlay.style.display = 'flex';
            }
            if (contentContainer) {
                contentContainer.classList.remove('visible');
            }
        } else {
            if (loginOverlay) {
                loginOverlay.style.display = 'none';
            }
            if (contentContainer) {
                contentContainer.classList.add('visible');
            }
        }
    }

    initializeEventListeners() {
        const txtPassword = document.getElementById('txtPassword');
        if (txtPassword) {
            txtPassword.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.validatePassword();
                }
            });
        }
    }
}

// Create global instance
const navigation = new Navigation();
