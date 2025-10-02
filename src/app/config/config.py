""" Module for reading jSON based config - differs from environment dependent config (.env)"""

import json
import os

def read_cors_config():
    """ Sets up a json.based config for the FastAPI app

    Raises:
        ValueError: Raised when a mandatory parameter is missing

    Returns:
        json_config['allowed_routes'] (List[str]): A list of allowed routes per CORS.
    """
    try:
        with open(os.getenv('CONFIG_FILE'), encoding='utf-8') as fp:
            json_config = json.load(fp)
        return json_config['allowed_routes']
    except ValueError as exc:
        raise ValueError('missing configuration \'allowed_routes\'. Please check the deploy pipeline and/or docs.') from exc