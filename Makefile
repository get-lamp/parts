.PHONY: seed, clean

seed:
	@pipenv run python -m scripts.seed

clean:
	@rm parts.db

run:
	@pipenv run python cli.py