# Offline energy export

`export_energy_data.py` is an offline data utility using `pandas` and `pymysql`,
separate from Home Assistant's `python_script:` services. It is not loaded by
`configuration.yaml`.

Its database/data-source settings belong to the local execution environment.
Do not infer deployment or scheduled execution from its presence in this folder.
