# utility functions for running fluke pipelines.
# Main backend to be used is the `targets` pacakge in R.


#' @title identifies if a dirname is ane xisting pipeline path.
#' @param ppl A String. name of pipeline
#' @return A list of the name of pipeline and  the full path of the pipeline.
#' @export
pipeline_script_path <- function(ppl) {
  full_dir_path <- rprojroot::find_rstudio_root_file("pipelines", ppl)
  pipeline_r_exists <- "pipeline.R" %in% basename(fs::dir_ls(full_dir_path))

  if (pipeline_r_exists) {
    return(
      list(name = ppl,
      path = file.path(full_dir_path, "pipeline.R"))
      )
  } else {
    return(NULL)
  }

}

#' @title get pipelines created under pipelines/
#' @return A \code{pipelines} object.
#' @export
get_pipelines <- function() {
  path_to_pipelines <- rprojroot::find_rstudio_root_file("pipelines")
  pipelines <-
    fs::dir_map(
    path_to_pipelines, fun = function(x) pipeline_script_path(basename(x)),
    type = "directory"
  )
  # remove nulls
  pipelines <- pipelines[lengths(pipelines) != 0]
  if (is.null(pipelines)) {
    stop("No pipelines exists! Consider creating one using
    `fluke pipeline create`")
  }

  return(structure(pipelines, class = "pipelines"))
}


#'@title prepare_targets generic method
#' @export
prepare_targets <- function(x, ...) {
  UseMethod("prepare_targets")
}


#' @title Prepares pipelines for eventual `targets::tar_make`.
#' @return A list of `tar_target` or `tar_target_raw`
#' objects from the `targets` package.
#' @export
prepare_targets.pipelines <- function(pipelines) {
  lapply(pipelines, function(ppl) source(ppl$path)$value)

}

#' @title get pipelines config, or specific config for pipeline
#' @param name name of pipeline. if NULL, returns whole pipelines config.
#' @export
pipelines_config <- function(name = NULL) {
  ppl_config_path <- rprojroot::find_rstudio_root_file(
    "config", "pipelines.yaml"
  )
  config <- yaml::read_yaml(ppl_config_path)

  if (is.null(config$pipelines$version)) {
    warning("No version found. Consider defining pipelines version in `config/pipelines.yaml`.")
  }
  if (!is.null(name)) {
    tryCatch(
      return(config[[name]]),
      error = function(e) {
        message(sprintf("no params set for pipeline '%s'.", name))
        return(NULL)
      }
    )
  }

  return(config)

}


#' @export
setup_pipelines <- function() {
  Sys.setenv(TAR_CONFIG = "config/targets.yaml")
  Sys.setenv(TAR_PROJECT = "main")

  config <- pipelines_config()
  ppl <- config$pipelines
  #derive pipelines store
  if (!is.null(ppl$version)) {
    ppl$store <- file.path("pipelines", "store", ppl$version)
  }
  ppl$version <- NULL
  ppl$script <- "pipelines/targets-pipelines.R"

  do.call(targets::tar_config_set, ppl)

}
