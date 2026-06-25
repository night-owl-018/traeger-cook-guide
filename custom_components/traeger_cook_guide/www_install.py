"""Copy the cook guide HTML from the integration package to /config/www/traeger_cook_guide/."""
from __future__ import annotations

import logging
import os
import shutil

from homeassistant.core import HomeAssistant

from .const import WWW_SUBDIR, HTML_FILENAME

_LOGGER = logging.getLogger(__name__)


def install_www_files(hass: HomeAssistant) -> None:
    """Copy HTML from inside the integration package to /config/www/traeger_cook_guide/.

    HACS only downloads custom_components/ — so the HTML lives alongside
    the Python files and we copy it out to www/ on first setup.
    """
    # HTML is bundled inside the integration package itself
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(pkg_dir, HTML_FILENAME)

    dst_dir = os.path.join(hass.config.config_dir, "www", WWW_SUBDIR)
    dst = os.path.join(dst_dir, HTML_FILENAME)

    os.makedirs(dst_dir, exist_ok=True)

    if not os.path.isfile(src):
        _LOGGER.error(
            "Traeger Cook Guide: HTML not found at %s — "
            "HACS may not have downloaded the integration correctly. "
            "Try removing and re-downloading in HACS.",
            src,
        )
        return

    shutil.copy2(src, dst)
    _LOGGER.info("Traeger Cook Guide: HTML installed to %s", dst)


def remove_www_files(hass: HomeAssistant) -> None:
    """Remove the www subdirectory on uninstall."""
    dst_dir = os.path.join(hass.config.config_dir, "www", WWW_SUBDIR)
    if os.path.isdir(dst_dir):
        shutil.rmtree(dst_dir, ignore_errors=True)
        _LOGGER.info("Traeger Cook Guide: removed www files at %s", dst_dir)
