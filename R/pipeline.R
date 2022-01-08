# utility functions for running fluke pipelines.
# Main backend to be used is the `targets` pacakge in R.


#' @title identifies if a dirname is ane xisting pipeline path.
#' @param ppl A String. name of pipeline
#' @return A list of the name of pipeline and  the full path of the pipeline.
#' @export
pipeline_script_path <- function(ppl) {
  full_dir_path <- here::here("pipelines", ppl)
  pipeline_r_exists <- "pipeline.R" %in% fs::dir_ls(full_dir_path)

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
  path_to_pipelines <- here::here("pipelines")
  pipelines <- unlist(
    fs::dir_map(
    path_to_pipelines, fun = pipeline_script_path, type = "directory"
    )
  )

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
  # create a new environment
  tar_env <- new.env()

  # source to new environment
  lapply(pipelines, function(ppl) source(ppl$path, local = tar_env))

  # return as list for `tar_make`
  return(as.list(tar_env))


}
