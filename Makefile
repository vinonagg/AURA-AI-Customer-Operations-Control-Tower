install:
	python -m pip install -r requirements.txt
run-api:
	PYTHONPATH=. uvicorn app.main:app --reload --port 8010
run-ui:
	AURA_API_URL=http://127.0.0.1:8010 PYTHONPATH=. streamlit run streamlit_app/app.py --server.port 8501
seed:
	PYTHONPATH=. python scripts/seed_demo.py
test:
	PYTHONPATH=. pytest -q
