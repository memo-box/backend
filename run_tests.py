#!/usr/bin/env python
import os
import sys
import django
import subprocess
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "memobox.settings"
    django.setup()

    # Check if we should run with pytest
    use_pytest = len(sys.argv) > 1 and sys.argv[1] == "--pytest"

    if use_pytest:
        # Run tests with pytest
        pytest_args = (
            sys.argv[2:] if len(sys.argv) > 2 else ["leitner/tests/", "ai/tests/"]
        )
        exit_code = subprocess.call(["pytest"] + pytest_args)
        sys.exit(exit_code)
    else:
        # Run tests with Django test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner()

        # List all test modules manually
        test_modules = [
            "leitner.tests.test_models",
            "leitner.tests.test_serializers",
            "leitner.tests.test_views",
            "leitner.tests.test_django",
            "ai.tests.test_serializers",
            "ai.tests.test_views",
            "ai.tests.test_django",
        ]

        failures = test_runner.run_tests(test_modules)
        sys.exit(bool(failures))
