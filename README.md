Ontology modeling app — refactor notes

- The original single-file application has been split into a small package `ontology_app`.
- The heavy `Ontology1.py` module no longer starts the QApplication at import time; it exposes a `main()` function.
- Use `python run.py` to launch the app.

Next steps (completed):
- Domain logic has been moved into `ontology_app/models.py`.
- Database code extracted to `ontology_app/storage.py` and initialised on import.
- Visualization helpers reside in `ontology_app/viz.py`.
- Minimal tests added under `tests/` and a `requirements.txt` created.

To run the application:
```bash
pip install -r requirements.txt
python run.py
```

Run the model tests with pytest:
```bash
pytest tests/test_models.py
```
