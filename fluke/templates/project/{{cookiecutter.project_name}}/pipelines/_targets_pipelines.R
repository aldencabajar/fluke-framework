# DO NOT EDIT, INITIALIZATION FILE FOR PIPELINES
local({
  library(fluke)

  # retrieve list of targets
  pipelines <- get_pipelines()
  prepare_targets(pipelines)

})

