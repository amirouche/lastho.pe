help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

init: ## Prepare the host sytem for development
	pip3 install --upgrade pipenv==2018.10.13
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev --skip-lock
	pipenv run pre-commit install --hook-type pre-push
	@echo "\033[95m\n\nYou may now run 'pipenv shell'.\n\033[0m"

check: ## Run tests
	make database-clear
	PYTHONHASHSEED=0 PYTHONPATH=$(PWD)/src/ pipenv run py.test -vvv --cov-config .coveragerc --cov-report html --cov-report xml --cov=lasthope src/tests/
	pipenv check
	pipenv run bandit --skip=B101 src/
	@echo "\033[95m\n\nYou may now run 'make lint'.\n\033[0m"

devback: ## Run application in development mode
	cd src && DEBUG=DEBUG adev runserver --livereload lasthope/main.py

devfront: ## Run the frontend


lint: ## Lint the code
	pipenv run pylama src/

doc: ## Build the documentation
	cd src/doc && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at src/doc/_build/html/index.html.\n\033[0m"

database-clear:  ## Remove all data from the database
	fdbcli --exec "writemode on; clearrange \x00 \xFF;"

todo: ## Things that should be done
	@grep -nR --color=always TODO src/

xxx: ## Things that require attention
	@grep -nR --color=always --before-context=2  --after-context=2 XXX src/

repl: ## ipython REPL inside source directory
	cd src && ipython
