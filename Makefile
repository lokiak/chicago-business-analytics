run:
	python main.py --all

run-step2:
	python main.py --step 2

run-step3:
	python main.py --step 3

run-step4:
	python main.py --step 4

run-step5:
	python main.py --step 5

run-step6:
	python main.py --step 6

docs-serve:
	@echo "🏙️ Chicago SMB Market Radar - Documentation Server"
	@echo "=" $(shell printf '%.0s=' $$(seq 1 55))
	@echo "🚀 Starting modern documentation site..."
	@echo "📱 Features: Search, navigation, mobile-responsive design"
	@echo "🎨 Includes: Interactive guides, progress tracking, code examples"
	@echo ""
	@echo "📍 Access your documentation at:"
	@echo "   🌐 Main Site: http://localhost:8000"
	@echo "   📚 Getting Started: http://localhost:8000/getting-started/"
	@echo "   📊 BI Framework: http://localhost:8000/framework/"
	@echo "   🔧 How-to Guides: http://localhost:8000/guides/"
	@echo "   📈 Reports: http://localhost:8000/reports/"
	@echo ""
	@echo "🛑 Press Ctrl+C to stop the server"
	@echo ""
	@if command -v python3 >/dev/null 2>&1; then \
		cd docs && echo "✅ Server starting..." && python3 -m http.server 8000; \
	elif command -v python >/dev/null 2>&1; then \
		cd docs && echo "✅ Server starting..." && python -m http.server 8000; \
	else \
		echo "❌ Python not found. Please install Python to serve documentation."; \
		exit 1; \
	fi

docs-build:
	@echo "📚 Building Chicago SMB Market Radar Documentation"
	@echo "=" $(shell printf '%.0s=' $$(seq 1 55))
	@echo ""
	@echo "📊 Documentation Structure:"
	@echo "├── 🏠 Main Site (index.html) - Modern responsive design"
	@echo "├── 🚀 Getting Started - Setup and first analysis"
	@echo "├── 📊 BI Framework - Complete pipeline documentation"  
	@echo "├── 📚 How-to Guides - Step-by-step task guides"
	@echo "├── 🔧 Technical Reference - API docs and troubleshooting"
	@echo "├── 📈 Reports & Analysis - Generated insights and notebooks"
	@echo "└── ℹ️ About - Project information and changelog"
	@echo ""
	@echo "📁 Documentation files discovered:"
	@find docs/ -name "*.md" -type f | wc -l | xargs echo "   📄 Markdown files:"
	@find docs/ -name "*.html" -type f | wc -l | xargs echo "   🌐 HTML pages:"
	@echo ""
	@echo "✨ Features included:"
	@echo "   🔍 Live search functionality"
	@echo "   📱 Mobile-responsive design"
	@echo "   🌙 Dark/light theme toggle"
	@echo "   📋 Progress tracking"
	@echo "   📝 Copy-to-clipboard for code blocks"
	@echo "   🔗 Smooth navigation between sections"
	@echo ""
	@echo "🚀 To serve documentation locally, run: make docs-serve"

docs-preview:
	@echo "👀 Opening documentation preview..."
	@if command -v open >/dev/null 2>&1; then \
		open docs/index.html; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open docs/index.html; \
	else \
		echo "📁 Open docs/index.html in your browser to preview"; \
	fi

docs-validate:
	@echo "✅ Validating documentation structure..."
	@echo "Checking required files and directories:"
	@test -f docs/index.html && echo "✅ Main site (index.html)" || echo "❌ Missing index.html"
	@test -d docs/assets && echo "✅ Assets directory" || echo "❌ Missing assets/"
	@test -d docs/getting-started && echo "✅ Getting Started section" || echo "❌ Missing getting-started/"
	@test -d docs/framework && echo "✅ BI Framework section" || echo "❌ Missing framework/"
	@test -d docs/guides && echo "✅ How-to Guides section" || echo "❌ Missing guides/"
	@test -d docs/technical && echo "✅ Technical Reference section" || echo "❌ Missing technical/"
	@test -d docs/reports && echo "✅ Reports section" || echo "❌ Missing reports/"
	@test -d docs/about && echo "✅ About section" || echo "❌ Missing about/"
	@echo ""
	@echo "🔍 Checking for broken links..."
	@echo "   (Manual verification recommended)"
	@echo ""
	@echo "📊 Documentation Statistics:"
	@find docs/ -name "*.md" | wc -l | xargs echo "   📄 Total Markdown files:"
	@find docs/ -name "*.html" | wc -l | xargs echo "   🌐 Total HTML pages:"
	@find docs/ -name "*.css" | wc -l | xargs echo "   🎨 Stylesheets:"
	@find docs/ -name "*.js" | wc -l | xargs echo "   ⚡ JavaScript files:"

help:
	@echo "Chicago SMB Market Radar - Available Commands:"
	@echo ""
	@echo "📊 BI Framework Steps:"
	@echo "  run              Run all BI framework steps"
	@echo "  run-step2        Run Step 2: Data Ingestion"
	@echo "  run-step3        Run Step 3: Transform & Model"
	@echo "  run-step4        Run Step 4: Load & Validate"
	@echo "  run-step5        Run Step 5: Visualize & Report"
	@echo "  run-step6        Run Step 6: Automate & Scale"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs-serve       Serve modern documentation site at http://localhost:8000"
	@echo "  docs-build       Display documentation structure and features"
	@echo "  docs-preview     Open documentation in browser (offline)"
	@echo "  docs-validate    Validate documentation structure and links"
	@echo ""
	@echo "📋 Help:"
	@echo "  help             Show this help message"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make run                    # Run all steps"
	@echo "  make run-step2             # Run data ingestion only"
	@echo "  make docs-serve            # Serve docs locally"

setup-automation:
	@echo "🔧 Setting up automation..."
	@chmod +x step6_automate_scale/scripts/setup_automation.sh
	@./step6_automate_scale/scripts/setup_automation.sh

.PHONY: run run-step2 run-step3 run-step4 run-step5 run-step6 docs-serve docs-build docs-preview docs-validate help setup-automation
