# Virtual environment directory
VENV_DIR = .venv

# Python executable to use
PYTHON = $(VENV_DIR)/bin/python

# The tools to use
PROTO_BITS   = $(PYTHON) tools/proto_bits.py
PROTOBUF_FMT = $(PYTHON) tools/protobuf_fmt.py

# Sphinx options
SPHINXOPTS    =
SPHINXBUILD   = $(VENV_DIR)/bin/sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
SPHINXTARGETS = html dirhtml singlehtml json latex latexpdf latexpdfja text \
                changes xml pseudoxml linkcheck

# Additional directories of interest
BITSSOURCEDIR = $(SOURCEDIR)/bits
BITSBUILDDIR  = $(BUILDDIR)/bits
PROTODIR      = $(SOURCEDIR)/protobuf

# Files of interest
BITSFILES = $(shell find $(BITSSOURCEDIR) -name '*.bits' -print | sed 's@.*/@@')

# Build HTML by default
all: html

$(VENV_DIR):
	virtualenv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt

$(BITSBUILDDIR):
	mkdir -p $(BITSBUILDDIR)

# Format protobuf files for prettiness
format: $(VENV_DIR)
	$(PROTOBUF_FMT) $(PROTODIR)/*.proto

bits: $(VENV_DIR) $(BITSBUILDDIR) $(BITSFILES:%.bits=$(BITSBUILDDIR)/%.txt)

clean:
	rm -rf $(BUILDDIR)
	rm -f $(SOURCEDIR)/protobuf/*~

# Construct plain text files from YAML descriptions of the bit layouts
# for some protocol elements
$(BITSBUILDDIR)/%.txt: $(BITSSOURCEDIR)/%.bits
	$(PROTO_BITS) --bare $< > $@

# Route all unknown targets to Sphinx with its "make mode" option.
$(SPHINXTARGETS): bits $(VENV_DIR)
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: all format bits clean
