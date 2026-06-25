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
    # Source: inside the integration package directory, one level up in /www/
    pkg_dir = os.path.dirname(__file__)
    src = os.path.join(pkg_dir, "..", "..", "www", HTML_FILENAME)
    src = os.path.normpath(src)

    dst_dir = os.path.join(hass.config.config_dir, "www", WWW_SUBDIR)
    dst = os.path.join(dst_dir, HTML_FILENAME)

    os.makedirs(dst_dir, exist_ok=True)

    if not os.path.isfile(src):
        _LOGGER.error(
            "Traeger Cook Guide: HTML source not found at %s — "
            "check HACS downloaded all files correctly",
            src,
        )
        return

    # Only copy if the destination is missing or the source is newer
    if not os.path.isfile(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
        shutil.copy2(src, dst)
        _LOGGER.info("Traeger Cook Guide: HTML installed to %s", dst)
    else:
        _LOGGER.debug("Traeger Cook Guide: HTML already up to date at %s", dst)


def remove_www_files(hass: HomeAssistant) -> None:
    """Remove the www directory on uninstall."""
    dst_dir = os.path.join(hass.config.config_dir, "www", WWW_SUBDIR)
    if os.path.isdir(dst_dir):
        shutil.rmtree(dst_dir, ignore_errors=True)
        _LOGGER.info("Traeger Cook Guide: removed www files at %s", dst_dir)
