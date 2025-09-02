# uv run -m ocean_report.main # took out the __name__ == "__main__" in main.py
uv run python -c "from ocean_report import run_report; run_report(run_email=False, test=True)"