"""Allows ``python -m hypeagent`` to invoke the run entrypoint."""

import sys

from hypeagent.main import main

if __name__ == "__main__":
    sys.exit(main())
