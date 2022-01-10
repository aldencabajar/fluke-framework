# DO NOT EDIT, INITIALIZATION FILE FOR PIPELINES
library(targets)
library(fluke)

# retrieve list of targets from pipeline.R in each <name_of_pipeline> directory.
pipelines <- get_pipelines()
prepare_targets(pipelines)
