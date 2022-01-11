##  CONFIGURATION (DO NOT EDIT BY HAND!)
library(targets)
library(fluke)
library({{cookiecutter.pkg_name}})

# you can reference params from `pipelines.yml`
# using <name_of_pipeline>$`name_of_field` accordingly.
{{cookiecutter.pipeline_name}} <- pipelines_config("{{cookiecutter.pipeline_name}}")

# START TARGETS PIPELINE HERE ----------------------------

