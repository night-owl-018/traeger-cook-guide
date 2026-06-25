"""Copy the cook guide HTML to /config/www/traeger_cook_guide/."""
from __future__ import annotations

import logging
import os
import shutil

from homeassistant.core import HomeAssistant

from .const import WWW_SUBDIR, HTML_FILENAME

_LOGGER = logging.getLogger(__name__)


def install_www_files(hass: HomeAssistant) -> None:
    """Synchronous — run via async_add_executor_job."""
    # HACS installs files into /config/custom_components/traeger_cook_guide/
    # The www/ folder in the repo gets placed two levels up from __file__
    # Path: /config/custom_components/traeger_cook_guide/__file__
    #  -> ../../www/traeger_cook_guide.html
    #  -> /config/www/traeger_cook_guide.html  (HACS places it here)
    pkg_dir = os.path.dirname(__file__)

    # Try multiple source locations — HACS can place www files differently
    candidates = [
        # HACS places repo root /www/ contents at /config/www/
        os.path.join(hass.config.config_dir, "www", HTML_FILENAME),
        # Relative from package: ../../www/filename
        os.path.normpath(os.path.join(pkg_dir, "..", "..", "www", HTML_FILENAME)),
        # Relative from package: ../www/filename
        os.path.normpath(os.path.join(pkg_dir, "..", "www", HTML_FILENAME)),
    ]

    src = None
    for candidate in candidates:
        _LOGGER.debug("Traeger Cook Guide: checking for HTML at %s", candidate)
        if os.path.isfile(candidate):
            src = candidate
            break

    dst_dir = os.path.join(hass.config.config_dir, "www", WWW_SUBDIR)
    dst = os.path.join(dst_dir, HTML_FILENAME)

    # If source is already at destination, nothing to do
    if src and os.path.normpath(src) == os.path.normpath(dst):
        _LOGGER.info("Traeger Cook Guide: HTML already at correct location %s", dst)
        return

    os.makedirs(dst_dir, exist_ok=True)

    if src is None:
        _LOGGER.error(
            "Traeger Cook Guide: HTML source not found in any of: %s",
            candidates,
        )
        return

    shutil.copy2(src, dst)
    _LOGGER.info("Traeger Cook Guide: HTML installed from %s to %s", src, dst)


def remove_www_files(hass: HomeAssistant) -> None:
    """Remove the www subdirectory on uninstall."""
    dst_dir = os.path.join(hass.config.config_dir, "www", WWW_SUBDIR)
    if os.path.isdir(dst_dir):
        shutil.rmtree(dst_dir, ignore_errors=True)
        _LOGGER.info("Traeger Cook Guide: removed www files at %s", dst_dir)
