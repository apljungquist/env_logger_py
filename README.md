# Env Logger

A replacement for the standard library `logging.basicConfig`, with some extra bells and whistles.

## Nice defaults

It uses subjectively nicer defaults e.g. by using a handler that colors the output.

## Multiple configuration sources
It allows users to override the configuration environment variables e.g. like

```bash
LOG_LEVEL=DEBUG \
LOG_FORMAT='%(levelname)8s %(message)s' \
env_logger demo
```

In general, the name of the environment variable follows the name of the basicConfig parameter and takes the same values.


## Ecosystem

The package is designed to be compatible with `rich` e.g. like

```python
import logging
import env_logger
import rich.logging

env_logger.configure(handlers=[rich.logging.RichHandler()])
logging.getLogger(__name__).info("Hello!")
```
