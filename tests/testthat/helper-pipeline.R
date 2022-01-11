# Helper functions for testing pipelines
ppl_cfg <- "config/pipelines.yaml"

set_pipelines_config <- function(object, env = parent.frame()) {
  # get previous config
  prev_config <- yaml::read_yaml(ppl_cfg)
  yaml::write_yaml(object, ppl_cfg)
  withr::defer({
    yaml::write_yaml(prev_config, ppl_cfg)
  },
  envir = env
  )
}

create_pipeline <- function(name, env = parent.frame()) {
  # get previous config
  prev_config <- yaml::read_yaml("config/pipelines.yaml")

  # write  pipelines.yml with version filled-in
  curr_config <- prev_config
  curr_config$store <- "test"
  yaml::write_yaml(curr_config, "config/pipelines.yaml")

  args <- c("pipeline", "create", name)
  system2("fluke", args)


  withr::defer({
    # delete pipeline folder
    fs::dir_delete(file.path("pipelines", name))
    # restore previous config
    yaml::write_yaml(prev_config, "config/pipelines.yaml")
  },
  envir = env)

}


write_to_pipeline_script <- function(
  pipeline, expr, new_file = NULL,
  env = parent.frame()) {

  expr_str <- deparse(substitute(expr))
  ppl <- fluke::pipeline_script_path(pipeline)
  ppl_dir <- dirname(ppl$path)

  # get old lines from script
  old_lines <- readLines(ppl$path)

  # append to pipeline.R or create a new file within the pipeline
  if (is.null(new_file)) {
    write(expr_str, ppl$path, append = TRUE)
  } else {
    new_file_path <- file.path(ppl_dir, new_file)
    write(expr_str, new_file_path)

  }
  withr::defer({
    #revert back to the old lines
    writeLines(old_lines, ppl$path)
    # delete new file if invoked
    if (!is.null(new_file)) {
      fs::file_delete(new_file_path)
    }
  },
  envir = env)

}


