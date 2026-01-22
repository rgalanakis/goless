install:
	pip install -r requirements-dev.txt

test:
	nosetests ./tests
