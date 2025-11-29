install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

run:
	python src/run.py "Analyze ROAS drop in last 7 days"

test:
	pytest -q

clean:
	rm -rf .venv __pycache__ reports logs