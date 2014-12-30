.PHONY: help lint phpcs phpunit test composer cleangit

help: # Show help
	@grep "^[[:alnum:]]*:" Makefile

pep8: # pep8 all py files
	pep8 Leck/

lint: # Lint (Compile...) all py files
	find ./Leck ./tests -name "*.py" -exec python -m py_compile {} \;

unittest: # Python unittest - tests dir
	PYTHONPATH=./Leck python tests/test_*.py

test: lint unittest
