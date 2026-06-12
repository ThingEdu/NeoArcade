.PHONY: install run run-sim test lint

install:
	python -m venv .venv && .venv/bin/pip install -e ".[dev]"

run:            ## chạy với phần cứng ThingBot
	.venv/bin/python -m neoarcade.app --profile thingbot

run-sim:        ## chạy bằng bàn phím (không cần phần cứng)
	.venv/bin/python -m neoarcade.app --profile keyboard

test:
	.venv/bin/python -m pytest -q

lint:
	.venv/bin/ruff check src tests
