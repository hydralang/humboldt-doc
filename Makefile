VENV_DIR = .venv

$(VENV_DIR):
	virtualenv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt
