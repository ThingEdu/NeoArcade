.PHONY: install run run-sim test lint

install:
	python -m venv .venv && .venv/bin/pip install -e ".[dev]"

run:            ## chạy với phần cứng ThingBot
	.venv/bin/python -m neoarcade.app --profile thingbot

hub:            ## Màn hình tổng — chọn game (launcher)
	.venv/bin/python -m neoarcade.hub

run-sim:        ## FlappyDe bằng bàn phím (không cần phần cứng)
	.venv/bin/python -m neoarcade.app --profile keyboard

run-dexe:       ## Đua Xe Dế bằng bàn phím (lái A/D, ←/→)
	.venv/bin/python -m neoarcade.dexe.app --profile keyboard

test:
	.venv/bin/python -m pytest -q

lint:
	.venv/bin/ruff check src tests
