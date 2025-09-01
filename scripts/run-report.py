import ocean_report
import os

RUN_EMAIL = os.getenv("RUN_EMAIL", "False").lower() == "true"
TEST = os.getenv("TEST", "False").lower() == "true"

def main():
    """
    Run Ocean report email
    """
    ocean_report.hello()
    ocean_report.main(run_email=RUN_EMAIL, test=TEST)
    return None


if __name__ == "__main__":
    main()
