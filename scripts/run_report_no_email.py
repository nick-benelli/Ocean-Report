"""Script to run the ocean report without email."""

import os

import ocean_report

RUN_EMAIL = False
TEST = os.getenv("TEST", "False").lower() == "true"


def main():
    """
    Run Ocean report without email
    """
    # Check to see if the package is installed
    ocean_report.hello()

    # Run Report
    ocean_report.run_report(run_email=RUN_EMAIL, test=TEST)


if __name__ == "__main__":
    main()
