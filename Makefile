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
	@echo "📊 BI Framework Steps:"
	@echo "  run              Run all BI framework steps"
	@echo "  run-step2        Run Step 2: Data Ingestion"
	@echo "  run-step3        Run Step 3: Transform & Model"
	@echo "  run-step4        Run Step 4: Load & Validate"
	@echo "  run-step5        Run Step 5: Visualize & Report"
	@echo "  run-step6        Run Step 6: Automate & Scale"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs-serve       Serve documentation locally at http://localhost:8000"
	@echo "  docs-build       Build documentation (Markdown files)"
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

.PHONY: run run-step2 run-step3 run-step4 run-step5 run-step6 docs-serve docs-build help setup-automation
