// Markdown Renderer for SMB Documentation
// Renders markdown files as pages instead of downloads

class MarkdownRenderer {
    constructor() {
        this.initializeRenderer();
        this.handleNavigation();
    }

    initializeRenderer() {
        // Import marked.js for markdown parsing
        if (!window.marked) {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
            script.onload = () => this.configureMark();
            document.head.appendChild(script);
        } else {
            this.configureMark();
        }
    }

    configureMark() {
        if (window.marked) {
            // Configure marked options
            marked.setOptions({
                breaks: true,
                gfm: true,
                headerIds: true,
                headerPrefix: 'section-'
            });
        }
    }

    handleNavigation() {
        // Override navigation links to render MD files as pages
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (!link) return;

            const href = link.getAttribute('href');
            if (!href) return;

            // Check if it's a markdown file or documentation link
            if (this.isDocumentationLink(href)) {
                e.preventDefault();
                this.loadDocumentationPage(href, link.textContent);
            }
        });

        // Handle browser back/forward
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.isDocumentation) {
                this.loadDocumentationPage(e.state.href, e.state.title, false);
            }
        });
    }

    isDocumentationLink(href) {
        // Check if the link points to documentation content
        const docPatterns = [
            /\.md$/,
            /\/getting-started\//,
            /\/framework\//,
            /\/guides\//,
            /\/technical\//,
            /\/reports\//,
            /\/about\//
        ];

        return docPatterns.some(pattern => pattern.test(href)) || 
               href.includes('/docs/') ||
               this.isInternalDocLink(href);
    }

    isInternalDocLink(href) {
        // Check if it's an internal documentation link
        return !href.startsWith('http') && 
               !href.startsWith('mailto:') && 
               !href.startsWith('tel:') &&
               href !== '#';
    }

    async loadDocumentationPage(href, title, updateHistory = true) {
        try {
            // Show loading state
            this.showLoadingState();

            // Convert href to actual file path
            const filePath = this.resolveFilePath(href);
            
            // Fetch the content
            const response = await fetch(filePath);
            
            if (!response.ok) {
                throw new Error(`Failed to load: ${response.status}`);
            }

            const content = await response.text();
            const isMarkdown = filePath.endsWith('.md');

            // Process and render content
            let html;
            if (isMarkdown) {
                html = await this.renderMarkdown(content);
            } else {
                html = content;
            }

            // Update the page
            this.updatePageContent(html, title);

            // Update URL and history
            if (updateHistory) {
                const newUrl = new URL(href, window.location.origin + '/docs/');
                history.pushState(
                    { isDocumentation: true, href, title }, 
                    title, 
                    newUrl.pathname
                );
            }

            // Update navigation active state
            this.updateActiveNavigation(href);

            // Update breadcrumbs
            this.updateBreadcrumbs(href, title);

            // Re-initialize features for new content
            this.initializeContentFeatures();

        } catch (error) {
            console.error('Failed to load documentation:', error);
            this.showErrorState(href, error.message);
        }
    }

    resolveFilePath(href) {
        // Convert navigation href to actual file path
        let filePath = href;

        // Remove leading slash
        if (filePath.startsWith('/')) {
            filePath = filePath.substring(1);
        }

        // Add docs/ prefix if not present
        if (!filePath.startsWith('docs/')) {
            filePath = 'docs/' + filePath;
        }

        // Convert directory paths to README.md or index.html
        if (filePath.endsWith('/')) {
            filePath += 'README.md';
        } else if (!filePath.includes('.')) {
            // Try .md first, then .html
            const basePath = filePath;
            filePath = basePath + '.md';
            
            // We'll try .md first in the fetch, if it fails, try .html
        }

        return filePath;
    }

    async renderMarkdown(content) {
        if (!window.marked) {
            // Fallback: render as plain text with basic formatting
            return `<pre>${content}</pre>`;
        }

        // Process the markdown
        const html = marked.parse(content);
        
        // Post-process to add classes and enhancements
        return this.enhanceRenderedHtml(html);
    }

    enhanceRenderedHtml(html) {
        // Create a temporary element to manipulate the HTML
        const temp = document.createElement('div');
        temp.innerHTML = html;

        // Add classes to elements
        temp.querySelectorAll('h1').forEach(h1 => {
            h1.classList.add('text-gradient');
        });

        temp.querySelectorAll('h2, h3').forEach(h => {
            h.classList.add('animate-slide-in-left');
        });

        temp.querySelectorAll('p, ul, ol').forEach(p => {
            p.classList.add('animate-fade-in');
        });

        temp.querySelectorAll('pre').forEach(pre => {
            pre.classList.add('card-enhanced');
        });

        temp.querySelectorAll('blockquote').forEach(bq => {
            bq.classList.add('glass');
        });

        return temp.innerHTML;
    }

    updatePageContent(html, title) {
        const mainContent = document.querySelector('.docs-content');
        if (mainContent) {
            mainContent.innerHTML = html;
            
            // Update page title
            document.title = `${title} - Chicago SMB Market Radar`;
        }
    }

    updateActiveNavigation(href) {
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to current link
        const activeLink = document.querySelector(`a[href="${href}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    updateBreadcrumbs(href, title) {
        const breadcrumb = document.querySelector('.breadcrumb');
        if (!breadcrumb) return;

        // Build breadcrumb path
        const parts = href.split('/').filter(part => part);
        const breadcrumbItems = [{ name: 'Home', href: '/' }];

        let currentPath = '';
        parts.forEach((part, index) => {
            currentPath += '/' + part;
            const name = part.charAt(0).toUpperCase() + part.slice(1).replace('-', ' ');
            breadcrumbItems.push({ name, href: currentPath });
        });

        // Update breadcrumb HTML
        breadcrumb.innerHTML = breadcrumbItems.map((item, index) => {
            if (index === breadcrumbItems.length - 1) {
                return `<li><span class="current">${item.name}</span></li>`;
            } else {
                return `<li><a href="${item.href}">${item.name}</a></li>`;
            }
        }).join('');
    }

    showLoadingState() {
        const mainContent = document.querySelector('.docs-content');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="loading-state animate-fade-in">
                    <div class="loading-spinner"></div>
                    <p>Loading documentation...</p>
                </div>
            `;
        }
    }

    showErrorState(href, message) {
        const mainContent = document.querySelector('.docs-content');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="error-state card-enhanced">
                    <h2>❌ Content Not Found</h2>
                    <p>Sorry, we couldn't load the requested documentation page.</p>
                    <div class="error-details">
                        <p><strong>Path:</strong> ${href}</p>
                        <p><strong>Error:</strong> ${message}</p>
                    </div>
                    <div class="error-actions">
                        <button onclick="window.location.reload()" class="btn-primary-enhanced">
                            Try Again
                        </button>
                        <a href="/" class="btn-secondary-enhanced">
                            Return Home
                        </a>
                    </div>
                </div>
            `;
        }
    }

    initializeContentFeatures() {
        // Re-initialize features for dynamically loaded content
        if (window.initializeCodeCopyButtons) {
            window.initializeCodeCopyButtons();
        }
        
        if (window.initializeTOC) {
            window.initializeTOC();
        }

        if (window.initializeAnimations) {
            window.initializeAnimations();
        }
    }
}

// Initialize the markdown renderer when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new MarkdownRenderer();
    });
} else {
    new MarkdownRenderer();
}