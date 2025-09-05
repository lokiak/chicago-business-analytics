// Enhanced functionality for Chicago SMB Market Radar documentation

document.addEventListener('DOMContentLoaded', function() {
    // Add copy buttons to code blocks
    addCopyButtons();
    
    // Initialize progress bars
    initializeProgressBars();
    
    // Add quick navigation features
    addQuickNavigation();
    
    // Initialize search enhancements
    enhanceSearch();
});

function addCopyButtons() {
    // Add copy functionality to code blocks
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const button = document.createElement('button');
        button.className = 'copy-code-button';
        button.textContent = 'Copy';
        button.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            padding: 4px 8px;
            background: rgba(0,0,0,0.7);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        `;
        
        button.addEventListener('click', () => {
            navigator.clipboard.writeText(block.textContent);
            button.textContent = 'Copied!';
            setTimeout(() => button.textContent = 'Copy', 2000);
        });
        
        const pre = block.parentElement;
        pre.style.position = 'relative';
        pre.appendChild(button);
    });
}

function initializeProgressBars() {
    // Animate progress indicators when they come into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target;
                progressBar.style.opacity = '1';
                progressBar.style.transform = 'translateY(0)';
            }
        });
    });
    
    document.querySelectorAll('.progress-indicator').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
}

function addQuickNavigation() {
    // Add "Back to top" functionality
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '↑ Top';
    backToTop.className = 'back-to-top';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 10px 15px;
        background: var(--chicago-blue, #0F4C81);
        color: white;
        border: none;
        border-radius: 25px;
        cursor: pointer;
        font-size: 14px;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(backToTop);
    
    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    // Show/hide back to top button
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTop.style.opacity = '1';
        } else {
            backToTop.style.opacity = '0';
        }
    });
}

function enhanceSearch() {
    // Add search keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
    
    // Add search suggestions
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        searchInput.placeholder = 'Search documentation (Ctrl+K)';
    }
}

// Analytics and user experience enhancements
function trackDocumentationUsage() {
    // Track page visits (implement according to your analytics needs)
    if (typeof gtag !== 'undefined') {
        gtag('event', 'page_view', {
            page_title: document.title,
            page_location: window.location.href
        });
    }
}

// Initialize on page load
trackDocumentationUsage();

// Add version indicator
function addVersionInfo() {
    const versionBadge = document.createElement('div');
    versionBadge.innerHTML = `
        <div style="
            position: fixed;
            bottom: 80px;
            right: 20px;
            background: rgba(0,0,0,0.1);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            color: #666;
            z-index: 999;
        ">
            Docs v1.0 | Updated: ${new Date().toLocaleDateString()}
        </div>
    `;
    document.body.appendChild(versionBadge);
}

// Add version info
addVersionInfo();