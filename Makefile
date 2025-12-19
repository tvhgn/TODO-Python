# Default Python version (you can change this as a fallback)
PYTHON = python

# Define a variable for the virtual environment
VENV = venv

# Create a virtual environment with a specified Python version
venv:
	$(PYTHON) -m venv $(VENV)

# Install dependencies from requirements.txt
install: 
	$(VENV)/bin/pip install -r requirements.txt

# Clean up unwanted files
clean:
	rm -rf __pycache__
	find . -name "*.pyc" -exec rm -f {} \;

# To run: `make clean` or `make test`
