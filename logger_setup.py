import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        py_handler = logging.FileHandler("app_info.log")
        py_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    py_handler.setFormatter(py_formatter)
    logger.addHandler(py_handler)
    
    return logger
