MARP := ./node_modules/.bin/marp

.PHONY: build pptx pdf watch preview setup help

help:
	@echo "Usage: make <command>"
	@echo ""
	@echo "  setup    Install Node.js (via Homebrew if needed) + npm deps"
	@echo "  build    Build HTML  → dist/slides.html"
	@echo "  pptx     Build PPTX  → dist/slides.pptx"
	@echo "  pdf      Build PDF   → dist/slides.pdf"
	@echo "  watch    Live-reload HTML while editing"
	@echo "  preview  Open presenter preview in browser"

setup:
	@if ! command -v node &>/dev/null; then \
		echo "Node.js not found. Installing via Homebrew..."; \
		if ! command -v brew &>/dev/null; then \
			echo "Homebrew not found. Install it from https://brew.sh and re-run 'make setup'."; \
			exit 1; \
		fi; \
		brew install node; \
	else \
		echo "Node.js $$(node --version) already installed."; \
	fi
	npm install

build:
	mkdir -p dist
	$(MARP) slides.md --allow-local-files --output dist/slides.html
	cp -r assets dist/
	cp -r theme dist/
	sed -i '' 's|</head>|<link rel="icon" type="image/png" href="theme/favicon.png"></head>|' dist/slides.html

pptx:
	mkdir -p dist
	$(MARP) slides.md --allow-local-files --pptx --output dist/slides.pptx

pdf:
	mkdir -p dist
	$(MARP) slides.md --allow-local-files --pdf --output dist/slides.pdf

watch:
	mkdir -p dist
	cp -r assets dist/
	cp -r theme dist/
	$(MARP) slides.md --allow-local-files --watch --output dist/slides.html

preview:
	$(MARP) slides.md --allow-local-files --preview
