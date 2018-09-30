# Virtual environment directory
VENV_DIR = .venv

# Sphinx options
SPHINXOPTS  =
SPHINXBUILD = $(VENV_DIR)/bin/sphinx-build
SOURCEDIR   = source
BUILDDIR    = build

# Set up help as the first target
help: $(VENV_DIR)
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

$(VENV_DIR):
	virtualenv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt

# Route all unknown targets to Sphinx with its "make mode" option.
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile
