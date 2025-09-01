run:
	python -m src.main

docs-serve:
	@echo "🚀 Starting documentation server..."
	@echo "📚 Serving documentation at http://localhost:8000"
	@echo "📁 Documentation directory: docs/"
	@echo "🛑 Press Ctrl+C to stop the server"
	@echo ""
	@if command -v python3 >/dev/null 2>&1; then \
		cd docs && python3 -m http.server 8000; \
	elif command -v python >/dev/null 2>&1; then \
		cd docs && python -m http.server 8000; \
	else \
		echo "❌ Python not found. Please install Python to serve documentation."; \
		exit 1; \
	fi

docs-build:
	@echo "📚 Building documentation..."
	@echo "✅ Documentation is already in Markdown format"
	@echo "📁 Documentation files:"
	@find docs/ -name "*.md" -type f | head -10
	@echo ""
	@echo "💡 To serve documentation locally, run: make docs-serve"

help:
	@echo "Chicago SMB Market Radar - Available Commands:"
	@echo ""
	@echo "📊 Data Pipeline:"
	@echo "  run              Run the main data pipeline"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs-serve       Serve documentation locally at http://localhost:8000"
	@echo "  docs-build       Build documentation (Markdown files)"
	@echo ""
	@echo "🔧 Automation:"
	@echo "  setup-automation Run automation setup script"
	@echo ""
	@echo "📋 Help:"
	@echo "  help             Show this help message"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make run                    # Run data pipeline"
	@echo "  make docs-serve            # Serve docs locally"
	@echo "  make setup-automation      # Set up automation"

setup-automation:
	@echo "🔧 Setting up automation..."
	@chmod +x scripts/setup_automation.sh
	@./scripts/setup_automation.sh

.PHONY: run docs-serve docs-build help setup-automation
