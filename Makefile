#################################################################################
# GLOBALS                                                                      #
#################################################################################

PROJECT_NAME := $(shell basename $(CURDIR))
PYTHON_VERSION ?= 3.10 # To change this type in the terminal: make conda_env PYTHON_VERSION=3.11

# Check if conda is available
ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Set up python interpreter environment - to delete an environment: conda env remove -n [ENV_NAME]
conda_env:
ifeq (True,$(HAS_CONDA))
	@echo "Detected conda, creating conda environment."
	conda create --name $(PROJECT_NAME) python=$(PYTHON_VERSION) 
endif

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

kernel:
	python -m ipykernel install --user --name=$(PROJECT_NAME)

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
	
setup: conda_env install kernel

## Run all tests
PARAMS = --depth 2 # default 2 - can be changed: make data_pipe PARAMS="--depth 2"
data_pipe:
	python collect_wiki_urls.py ${PARAMS}
	python scrape_wiki_articles.py ${PARAMS}
	python process_and_store.py ${PARAMS}