# Env Logger

A replacement for the standard library `logging.basicConfig`, with some extra bells and whistles.


## Value proposition

### Nice defaults

It uses subjectively nicer defaults e.g. by using a handler that colors the output.

### Multiple configuration sources
It allows users to override the configuration environment variables e.g. like

```bash
LOG_LEVEL=DEBUG \
LOG_FORMAT='%(levelname)8s %(message)s' \
env_logger demo
```

In general, the name of the environment variable follows the name of the basicConfig parameter and takes the same values.


### Ecosystem

The package is designed to be compatible with `rich` e.g. like

```python
import logging
import env_logger
import rich.logging

env_logger.configure(handlers=[rich.logging.RichHandler()])
logging.getLogger(__name__).info("Hello!")
```

## Contribute

For Linux like environments the ambition is that setting up a development environment should be as easy as

```bash
source ./init_env.sh
make install_deps_py
```

Important workflows are documented in the [Makefile](./Makefile) and can be listed with `make help`.

### Prerequisites

- Python e.g. by
  1. installing pyenv following these [instructions](https://github.com/pyenv/pyenv#installation), and
  2. installing the targeted python version(s) like `pyenv install`
