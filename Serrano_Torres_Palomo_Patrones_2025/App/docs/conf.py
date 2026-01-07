import os
import sys
from datetime import datetime

# Add project src directory to sys.path so autodoc can import modules
sys.path.insert(0, os.path.abspath('../src'))

project = "PS-LAB2025"
author = ""
release = "0.0"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'

autosummary_generate = True
autodoc_typehints = 'description'
