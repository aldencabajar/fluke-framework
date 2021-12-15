##  CONFIGURATION (DO NOT EDIT BY HAND!)
library(targets)
path_to_pipeline <- here::here("pipelines", "{{cookiecutter.pipeline_name}}")
config <- file.path(path_to_pipeline, "pipeline.yml")

# you can reference settings from `pipeline.yml`
# using pipeline$`name_of_field` accordingly.
pipeline <- yaml::yaml.load_file(config)

# START TARGETS PIPELINE HERE ----------------------------
