# Contribuir

Usa Python 3.14 y un entorno virtual:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python -m pytest -q
.venv/bin/ruff check custom_components tests scripts
.venv/bin/python scripts/build_release.py
```

Añade pruebas cuando cambies el comportamiento. Usa respuestas ficticias en los tests; no incluyas credenciales ni datos reales de cuentas.

La integración utiliza OAuth y la renovación nativa de HA. Evita implementar un renovador paralelo o guardar tokens fuera de HA.
