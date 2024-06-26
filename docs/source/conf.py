# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

sys.path.append(os.path.abspath(os.path.join('..', '..', 'src')))
print(sys.path)
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'HW14'
copyright = '2024, DmytroT'
author = 'DmytroT'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = ['db.py', 'settings.py', 'migrations', 'alembic*',
                    'faker_db_filler.py', '*sqlite', '*.env']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
