class PromptGallery {
    constructor() {
        this.prompts = {
            basic: [],
            advanced: []
        };
        this.init();
    }

    init() {
        // Load prompts from the example sections
        const basicPrompts = document.querySelectorAll('.basic-queries li');
        const advancedPrompts = document.querySelectorAll('.advanced-queries li');
        
        basicPrompts.forEach(prompt => {
            this.prompts.basic.push({
                text: prompt.textContent,
                type: 'basic'
            });
        });

        advancedPrompts.forEach(prompt => {
            this.prompts.advanced.push({
                text: prompt.textContent,
                type: 'advanced'
            });
        });

        this.setupFilter();
        this.renderPrompts();
    }

    setupFilter() {
        const filterSelect = document.getElementById('prompt-filter');
        filterSelect.addEventListener('change', (e) => {
            this.renderPrompts(e.target.value);
        });
    }

    renderPrompts(type = 'all') {
        const basicSection = document.querySelector('.basic-queries').closest('.prompt-section');
        const advancedSection = document.querySelector('.advanced-queries').closest('.prompt-section');
        const basicContainer = document.querySelector('.basic-queries');
        const advancedContainer = document.querySelector('.advanced-queries');

        // Clear existing content
        basicContainer.innerHTML = '';
        advancedContainer.innerHTML = '';

        // Show/hide sections based on filter
        if (type === 'all') {
            basicSection.style.display = 'block';
            advancedSection.style.display = 'block';
        } else {
            basicSection.style.display = type === 'basic' ? 'block' : 'none';
            advancedSection.style.display = type === 'advanced' ? 'block' : 'none';
        }

        // Filter and render prompts
        Object.entries(this.prompts).forEach(([promptType, promptList]) => {
            if (type !== 'all' && type !== promptType) return;

            const container = promptType === 'basic' ? basicContainer : advancedContainer;
            const ol = document.createElement('ol');
            
            promptList.forEach(prompt => {
                const li = document.createElement('li');
                li.textContent = prompt.text;
                
                // Add click animation and copy functionality
                li.addEventListener('click', async (e) => {
                    // Add click animation
                    li.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        li.style.transform = 'translateY(-2px)';
                    }, 100);

                    await this.copyToClipboard(prompt.text);
                    
                    // Reset transform after animation
                    setTimeout(() => {
                        li.style.transform = '';
                    }, 300);
                });

                // Add hover effect for better UX
                li.addEventListener('mouseenter', () => {
                    li.style.transform = 'translateY(-2px)';
                });

                li.addEventListener('mouseleave', () => {
                    li.style.transform = '';
                });

                ol.appendChild(li);
            });

            container.appendChild(ol);
        });

        // Update counters
        this.updateCounters();
    }

    updateCounters() {
        const basicCount = document.querySelector('.basic-count');
        const advancedCount = document.querySelector('.advanced-count');

        const visibleBasic = document.querySelectorAll('.basic-queries li').length;
        const visibleAdvanced = document.querySelectorAll('.advanced-queries li').length;

        basicCount.textContent = `(${visibleBasic} prompts)`;
        advancedCount.textContent = `(${visibleAdvanced} prompts)`;
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('✓ Prompt copied to clipboard!');
        } catch (err) {
            this.showToast('❌ Failed to copy prompt');
        }
    }

    showToast(message) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.add('show');
        
        // Remove any existing timeout
        if (this.toastTimeout) {
            clearTimeout(this.toastTimeout);
        }
        
        // Set new timeout
        this.toastTimeout = setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PromptGallery();
});
