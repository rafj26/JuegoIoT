"""Configuracion de Sphinx para la documentacion del proyecto."""
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "Sistema de Seguridad IoT"
author = "rafj26"
copyright = "2025, rafj26"
release = "1.0"
language = "es"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# Tkinter puede no estar instalado donde se genera la documentacion
autodoc_mock_imports = ["tkinter"]
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_preserve_defaults = True

napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_title = "Sistema de Seguridad IoT"
html_static_path = []
