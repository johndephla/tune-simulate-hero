
import time
import random
import os
import logging

logger = logging.getLogger(__name__)

def random_wait(min_seconds=0.5, max_seconds=2.0):
    """Wait for a random amount of time to simulate human behavior"""
    wait_time = random.uniform(min_seconds, max_seconds)
    time.sleep(wait_time)
    return wait_time

def ensure_dir_exists(directory):
    """Ensure that the specified directory exists"""
    if not os.path.exists(directory):
        logger.info(f"Creating directory: {directory}")
        os.makedirs(directory)
    return directory
