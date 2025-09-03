// Chicago SMB Market Radar Documentation Scripts

document.addEventListener('DOMContentLoaded', function() {
    // Initialize enhanced theme system first
    initializeEnhancedThemeSystem();
    
    // Initialize original features
    initializeNavigation();
    initializeProgressTracking();
    initializeSearchFunctionality();
    initializeThemeToggle();
    initializeCodeCopyButtons();
    initializeScrollEffects();

    // Initialize modern documentation features
    initializeModernDocs();

    // Initialize advanced features
    initializeAdvancedNavigation();
    
    // Apply animations
    initializeAnimations();
});

// Enhanced Theme System from Portfolio
function initializeEnhancedThemeSystem() {
    // Create theme toggle button
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle';
    themeToggle.setAttribute('aria-label', 'Toggle theme');
    themeToggle.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle class="sun" cx="12" cy="12" r="5"></circle>
            <line class="sun" x1="12" y1="1" x2="12" y2="3"></line>
            <line class="sun" x1="12" y1="21" x2="12" y2="23"></line>
            <line class="sun" x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line class="sun" x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line class="sun" x1="1" y1="12" x2="3" y2="12"></line>
            <line class="sun" x1="21" y1="12" x2="23" y2="12"></line>
            <line class="sun" x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line class="sun" x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            <path class="moon" style="display: none;" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
    `;
    
    document.body.appendChild(themeToggle);
    
    // Get stored theme preference
    const storedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Apply initial theme
    if (storedTheme) {
        setTheme(storedTheme);
    } else if (prefersDark) {
        setTheme('dark');
    } else {
        setTheme('light');
    }
    
    // Theme toggle click handler
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

function setTheme(theme) {
    const html = document.documentElement;
    const themeToggle = document.querySelector('.theme-toggle');
    
    if (theme === 'dark') {
        html.classList.add('dark');
        html.classList.remove('light');
        if (themeToggle) {
            themeToggle.querySelector('.sun').style.display = 'none';
            themeToggle.querySelector('.moon').style.display = 'block';
        }
    } else {
        html.classList.add('light');
        html.classList.remove('dark');
        if (themeToggle) {
            themeToggle.querySelector('.sun').style.display = 'block';
            themeToggle.querySelector('.moon').style.display = 'none';
        }
    }
    
    localStorage.setItem('theme', theme);
}

// Initialize animations
function initializeAnimations() {
    // Add entrance animations to elements
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -10% 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.card, .feature-card, .step-card, h2, h3').forEach(el => {
        observer.observe(el);
    });
    
    // Add slide-up animation to main content
    const mainContent = document.querySelector('.docs-content, .main-content');
    if (mainContent) {
        mainContent.classList.add('animate-slide-up');
    }
}

// Advanced Navigation with Dropdowns
function initializeAdvancedNavigation() {
    // Add dropdown functionality to navigation sections
    const navSections = document.querySelectorAll('.nav-section');
    
    navSections.forEach(section => {
        const title = section.querySelector('.nav-section-title');
        const navList = section.querySelector('.nav-list');
        
        if (title && navList) {
            // Add collapse/expand functionality
            title.style.cursor = 'pointer';
            title.setAttribute('aria-expanded', 'true');
            title.setAttribute('role', 'button');
            title.setAttribute('tabindex', '0');
            
            // Add collapse icon
            const icon = title.querySelector('i');
            if (icon) {
                const chevron = document.createElement('i');
                chevron.className = 'fas fa-chevron-down nav-chevron';
                chevron.style.marginLeft = 'auto';
                chevron.style.transition = 'transform 0.3s ease';
                title.appendChild(chevron);
            }
            
            // Click handler for collapse/expand
            title.addEventListener('click', function() {
                const isExpanded = title.getAttribute('aria-expanded') === 'true';
                const chevron = title.querySelector('.nav-chevron');
                
                if (isExpanded) {
                    navList.style.maxHeight = '0';
                    navList.style.overflow = 'hidden';
                    title.setAttribute('aria-expanded', 'false');
                    if (chevron) chevron.style.transform = 'rotate(-90deg)';
                } else {
                    navList.style.maxHeight = navList.scrollHeight + 'px';
                    navList.style.overflow = 'visible';
                    title.setAttribute('aria-expanded', 'true');
                    if (chevron) chevron.style.transform = 'rotate(0deg)';
                }
            });
            
            // Keyboard handler
            title.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    title.click();
                }
            });
            
            // Initially set max-height for smooth transitions
            navList.style.transition = 'max-height 0.3s ease';
            navList.style.maxHeight = navList.scrollHeight + 'px';
        }
    });
}

// Enhanced search with better UX
function initializeEnhancedSearch() {
    const searchInput = document.getElementById('docsSearch');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput || !searchResults) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }
        
        // Debounce search
        searchTimeout = setTimeout(() => {
            performEnhancedSearch(query);
        }, 300);
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
}

function performEnhancedSearch(query) {
    const searchResults = document.getElementById('searchResults');
    if (!searchResults) return;
    
    // Mock search results - in production this would query your content
    const mockResults = [
        { title: 'Getting Started Guide', url: '/getting-started/', excerpt: 'Learn how to set up and run your first analysis' },
        { title: 'BI Framework Overview', url: '/framework/', excerpt: 'Complete guide to our business intelligence framework' },
        { title: 'Great Expectations Integration', url: '/guides/great-expectations.html', excerpt: 'Step-by-step guide for data validation' },
        { title: 'Data Cleaning Guide', url: '/guides/data-cleaning.html', excerpt: 'Manual and automated data cleaning techniques' },
        { title: 'API Reference', url: '/technical/api-reference.html', excerpt: 'Complete API documentation' }
    ].filter(item => 
        item.title.toLowerCase().includes(query.toLowerCase()) ||
        item.excerpt.toLowerCase().includes(query.toLowerCase())
    );
    
    if (mockResults.length === 0) {
        searchResults.innerHTML = '<div class="search-no-results">No results found</div>';
    } else {
        searchResults.innerHTML = mockResults.map(result => `
            <a href="${result.url}" class="search-result-item">
                <div class="search-result-title">${result.title}</div>
                <div class="search-result-excerpt">${result.excerpt}</div>
            </a>
        `).join('');
    }
    
    searchResults.style.display = 'block';
}

// Modern Documentation Features
function initializeModernDocs() {
    if (document.body.classList.contains('docs-layout')) {
        initializeSidebar();
        initializeEnhancedSearch();
        initializeTOC();
        initializeBreadcrumbs();
        initializePageNavigation();
        initializeActiveNavigation();
        initializeEnhancedBackToTop();
    }
}

// Navigation Enhancement
function initializeNavigation() {
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Highlight current navigation item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === currentPath.split('/').pop()) {
            link.classList.add('active');
        }
    });

    // Mobile navigation toggle
    const mobileToggle = document.querySelector('.mobile-nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('show');
            mobileToggle.classList.toggle('active');
        });
    }
}

// Progress Tracking
function initializeProgressTracking() {
    const progressItems = document.querySelectorAll('.progress-item');
    const totalItems = progressItems.length;
    const completedItems = document.querySelectorAll('.status-completed').length;
    const partialItems = document.querySelectorAll('.status-partial').length;

    // Calculate overall progress
    const progress = ((completedItems + (partialItems * 0.5)) / totalItems * 100).toFixed(0);

    // Update progress bar if exists
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.style.width = progress + '%';
        progressBar.textContent = progress + '%';
    }

    // Add progress indicator to page title
    const progressIndicator = document.querySelector('.progress-indicator');
    if (progressIndicator) {
        progressIndicator.textContent = `${progress}% Complete`;
    }
}

// Search Functionality
function initializeSearchFunctionality() {
    const searchInput = document.querySelector('#doc-search');
    const searchResults = document.querySelector('.search-results');

    if (!searchInput || !searchResults) return;

    let searchIndex = [];

    // Build search index from all navigation links
    document.querySelectorAll('.card-links a').forEach(link => {
        searchIndex.push({
            title: link.textContent.trim(),
            url: link.getAttribute('href'),
            category: link.closest('.card').querySelector('h3').textContent.trim()
        });
    });

    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();

        if (query.length < 2) {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
            return;
        }

        const matches = searchIndex.filter(item =>
            item.title.toLowerCase().includes(query) ||
            item.category.toLowerCase().includes(query)
        ).slice(0, 8);

        if (matches.length > 0) {
            searchResults.innerHTML = matches.map(match =>
                `<a href="${match.url}" class="search-result-item">
                    <strong>${highlightMatch(match.title, query)}</strong>
                    <span class="search-category">${match.category}</span>
                </a>`
            ).join('');
            searchResults.style.display = 'block';
        } else {
            searchResults.innerHTML = '<div class="no-results">No results found</div>';
            searchResults.style.display = 'block';
        }
    });

    // Hide search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });

    function highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
}

// Theme Toggle
function initializeThemeToggle() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (!themeToggle) return;

    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);

    themeToggle.addEventListener('click', () => {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update theme toggle icon
        themeToggle.textContent = newTheme === 'light' ? '🌙' : '☀️';
    });

    // Set initial icon
    themeToggle.textContent = currentTheme === 'light' ? '🌙' : '☀️';
}

// Code Copy Buttons
function initializeCodeCopyButtons() {
    document.querySelectorAll('.code-block').forEach(codeBlock => {
        // Skip if already has copy button
        if (codeBlock.querySelector('.copy-button')) return;

        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.textContent = 'Copy';
        copyButton.title = 'Copy to clipboard';

        copyButton.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(codeBlock.textContent);
                copyButton.textContent = 'Copied!';
                copyButton.classList.add('copied');

                setTimeout(() => {
                    copyButton.textContent = 'Copy';
                    copyButton.classList.remove('copied');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy text: ', err);
                copyButton.textContent = 'Failed';
                setTimeout(() => {
                    copyButton.textContent = 'Copy';
                }, 2000);
            }
        });

        // Position button
        codeBlock.style.position = 'relative';
        codeBlock.appendChild(copyButton);
    });
}

// Scroll Effects
function initializeScrollEffects() {
    // Fade in animation observer
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe all cards and major sections
    document.querySelectorAll('.card, .quick-start, .progress-section').forEach(el => {
        observer.observe(el);
    });

    // Back to top button
    const backToTop = document.createElement('button');
    backToTop.className = 'back-to-top';
    backToTop.innerHTML = '↑';
    backToTop.title = 'Back to top';
    backToTop.style.display = 'none';

    document.body.appendChild(backToTop);

    backToTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Show/hide back to top button
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTop.style.display = 'flex';
        } else {
            backToTop.style.display = 'none';
        }
    });
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add additional CSS for dynamic elements
const additionalCSS = `
.copy-button {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #e2e8f0;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s ease;
    opacity: 0.7;
}

.copy-button:hover {
    opacity: 1;
    background: rgba(255, 255, 255, 0.2);
}

.copy-button.copied {
    background: rgba(40, 167, 69, 0.2);
    border-color: rgba(40, 167, 69, 0.4);
}

.back-to-top {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 50px;
    height: 50px;
    background: var(--primary-gradient);
    color: white;
    border: none;
    border-radius: 50%;
    font-size: 1.2rem;
    cursor: pointer;
    box-shadow: var(--shadow);
    transition: var(--transition);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.back-to-top:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
}

.search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--card-background);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-hover);
    max-height: 300px;
    overflow-y: auto;
    z-index: 1000;
    display: none;
}

.search-result-item {
    display: block;
    padding: 1rem;
    text-decoration: none;
    color: var(--text-color);
    border-bottom: 1px solid var(--border-color);
    transition: var(--transition);
}

.search-result-item:hover {
    background: var(--background-color);
}

.search-result-item strong {
    display: block;
    font-weight: 600;
}

.search-category {
    font-size: 0.8rem;
    color: var(--text-muted);
}

.notification {
    position: fixed;
    top: 2rem;
    right: 2rem;
    padding: 1rem 1.5rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-hover);
    z-index: 2000;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    max-width: 300px;
}

.notification.show {
    transform: translateX(0);
}

.notification-info {
    background: var(--primary-color);
    color: white;
}

.notification-success {
    background: var(--success-color);
    color: white;
}

.notification-error {
    background: var(--danger-color);
    color: white;
}

mark {
    background: rgba(102, 126, 234, 0.2);
    color: var(--primary-color);
    padding: 0.1rem 0.2rem;
    border-radius: 2px;
}
`;

// Inject additional CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalCSS;
document.head.appendChild(styleSheet);

// =================================================================
// MODERN DOCUMENTATION FEATURES
// =================================================================

// Sidebar Management
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('docsSidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');

            // Close sidebar when clicking outside on mobile
            if (sidebar.classList.contains('open')) {
                document.addEventListener('click', handleOutsideClick);
            }
        });
    }
}

function handleOutsideClick(event) {
    const sidebar = document.getElementById('docsSidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (sidebar && !sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
        sidebar.classList.remove('open');
        document.removeEventListener('click', handleOutsideClick);
    }
}

// Enhanced Search Functionality
function initializeEnhancedSearch() {
    const searchInput = document.getElementById('docsSearch');
    const searchResults = document.getElementById('searchResults');

    if (searchInput && searchResults) {
        let searchIndex = buildSearchIndex();

        searchInput.addEventListener('input', debounce((e) => {
            performSearch(e.target.value, searchIndex, searchResults);
        }, 300));

        searchInput.addEventListener('focus', () => {
            if (searchInput.value.trim()) {
                searchResults.style.display = 'block';
            }
        });

        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });

        // Keyboard navigation for search results
        searchInput.addEventListener('keydown', (e) => {
            handleSearchKeyboard(e, searchResults);
        });
    }
}

function buildSearchIndex() {
    const searchIndex = [];
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const section = link.closest('.nav-section');
        const category = section ? section.querySelector('.nav-section-title').textContent.trim() : 'General';

        searchIndex.push({
            title: link.textContent.trim(),
            url: link.getAttribute('href'),
            category: category,
            keywords: link.textContent.toLowerCase().split(/\s+/).filter(word => word.length > 2)
        });
    });

    return searchIndex;
}

function performSearch(query, searchIndex, searchResults) {
    if (!query.trim()) {
        searchResults.style.display = 'none';
        return;
    }

    const results = searchIndex.filter(item => {
        const searchTerm = query.toLowerCase();
        return item.title.toLowerCase().includes(searchTerm) ||
               item.keywords.some(keyword => keyword.includes(searchTerm));
    }).slice(0, 8);

    displaySearchResults(results, query, searchResults);
}

function displaySearchResults(results, query, searchResults) {
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="search-result-item"><div class="search-result-title">No results found</div></div>';
    } else {
        searchResults.innerHTML = results.map(result => `
            <a href="${result.url}" class="search-result-item">
                <div class="search-result-title">${highlightText(result.title, query)}</div>
                <div class="search-result-excerpt">${result.category}</div>
            </a>
        `).join('');
    }

    searchResults.style.display = 'block';
}

function highlightText(text, query) {
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function handleSearchKeyboard(e, searchResults) {
    const items = searchResults.querySelectorAll('.search-result-item');

    if (e.key === 'Enter') {
        const firstResult = items[0];
        if (firstResult && firstResult.href) {
            window.location.href = firstResult.href;
        }
    } else if (e.key === 'Escape') {
        searchResults.style.display = 'none';
    }
}

// Table of Contents
function initializeTOC() {
    const tocNav = document.getElementById('tocNav');
    const content = document.querySelector('.docs-content');

    if (!tocNav || !content) return;

    const headings = content.querySelectorAll('h1, h2, h3, h4');
    const toc = Array.from(headings).map((heading, index) => {
        const id = heading.id || `heading-${index}`;
        if (!heading.id) {
            heading.id = id;
        }

        return {
            id,
            text: heading.textContent,
            level: parseInt(heading.tagName.charAt(1))
        };
    });

    renderTOC(tocNav, toc);
    initializeIntersectionObserver(headings);
}

function renderTOC(container, toc) {
    if (toc.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem;">No headings found</p>';
        return;
    }

    const tocHTML = toc.map(item => `
        <li class="level-${item.level}">
            <a href="#${item.id}" data-toc-target="${item.id}">${item.text}</a>
        </li>
    `).join('');

    container.innerHTML = `<ul>${tocHTML}</ul>`;

    // Add click handlers for smooth scrolling
    container.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.getElementById(link.getAttribute('data-toc-target'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                history.pushState(null, null, `#${target.id}`);
            }
        });
    });
}

function initializeIntersectionObserver(headings) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const id = entry.target.id;
            const tocLink = document.querySelector(`[data-toc-target="${id}"]`);

            if (tocLink) {
                if (entry.isIntersecting) {
                    // Remove active from all TOC links
                    document.querySelectorAll('[data-toc-target]').forEach(link => {
                        link.classList.remove('active');
                    });

                    // Add active to current link
                    tocLink.classList.add('active');
                }
            }
        });
    }, {
        rootMargin: '-20px 0px -80% 0px'
    });

    headings.forEach(heading => observer.observe(heading));
}

// Breadcrumbs
function initializeBreadcrumbs() {
    const breadcrumbNav = document.getElementById('breadcrumbNav');
    if (!breadcrumbNav) return;

    const pathSegments = window.location.pathname.split('/').filter(segment => segment);
    const breadcrumbs = [{ name: 'Home', url: '/' }];

    let currentPath = '';
    pathSegments.forEach((segment, index) => {
        currentPath += `/${segment}`;
        const name = formatBreadcrumbName(segment);

        if (index === pathSegments.length - 1) {
            breadcrumbs.push({ name, url: null }); // Current page
        } else {
            breadcrumbs.push({ name, url: currentPath });
        }
    });

    renderBreadcrumbs(breadcrumbNav, breadcrumbs);
}

function formatBreadcrumbName(segment) {
    return segment
        .replace(/[-_]/g, ' ')
        .replace(/\.(html|md)$/, '')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function renderBreadcrumbs(container, breadcrumbs) {
    const breadcrumbHTML = breadcrumbs.map(crumb => {
        if (crumb.url) {
            return `<li><a href="${crumb.url}">${crumb.name}</a></li>`;
        } else {
            return `<li><span>${crumb.name}</span></li>`;
        }
    }).join('');

    const breadcrumbList = container.querySelector('.breadcrumb');
    if (breadcrumbList) {
        breadcrumbList.innerHTML = breadcrumbHTML;
    }
}

// Page Navigation
function initializePageNavigation() {
    const navLinks = Array.from(document.querySelectorAll('.nav-link'));
    const currentIndex = navLinks.findIndex(link =>
        link.getAttribute('href') === window.location.pathname
    );

    if (currentIndex !== -1) {
        const prevPage = document.getElementById('prevPage');
        const nextPage = document.getElementById('nextPage');

        if (prevPage && currentIndex > 0) {
            const prevLink = navLinks[currentIndex - 1];
            prevPage.href = prevLink.getAttribute('href');
            prevPage.querySelector('.page-nav-title').textContent = prevLink.textContent;
            prevPage.style.display = 'flex';
        }

        if (nextPage && currentIndex < navLinks.length - 1) {
            const nextLink = navLinks[currentIndex + 1];
            nextPage.href = nextLink.getAttribute('href');
            nextPage.querySelector('.page-nav-title').textContent = nextLink.textContent;
            nextPage.style.display = 'flex';
        }
    }
}

// Active Navigation
function initializeActiveNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');

            // Scroll to active item in sidebar
            const sidebar = document.getElementById('docsSidebar');
            if (sidebar && link.offsetTop) {
                sidebar.scrollTop = link.offsetTop - sidebar.offsetHeight / 2;
            }
        }
    });
}

// Enhanced Back to Top
function initializeEnhancedBackToTop() {
    const backToTop = document.getElementById('backToTop');
    if (!backToTop) return;

    const toggleVisibility = () => {
        if (window.pageYOffset > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    };

    window.addEventListener('scroll', throttle(toggleVisibility, 100));

    backToTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}
