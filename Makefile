.PHONY: seed, clean, test, coverage

seed:
	@pipenv run python -m scripts.seed

clean:
	@rm parts.db

run:
	@pipenv run python cli.py

test:
	@pipenv run python -m pytest tests/ -v

coverage:
	@pipenv run python -m pytest tests/ -v \
		--cov=parts \
		--cov-report=term-missing \
		--cov-report=html