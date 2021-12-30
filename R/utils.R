# UTILITY FUNCTIONS

#' @title Return the package name in a fluke projejct.
#' @export
get_pkg_name <- function() {
  proj_config_path <- rprojroot::find_rstudio_root_file(
    "config", "project.yaml"
  )
  proj_config <- yaml::read_yaml(proj_config_path)
  return(proj_config$pkg_name)
}

#' @title Return path to package.
#'@export
get_pkg_file_path <- function() {
  return(
      rprojroot::find_rstudio_root_file(
      "src", get_pkg_name()
    )
  )
}

#' @title Get project metadata from `config/project.yaml`
#' @export
get_project_config <- function() {
  proj_config_path <- rprojroot::find_rstudio_root_file(
    "config", "project.yaml"
  )
  proj_config <- yaml::read_yaml(proj_config_path)
  return(proj_config)
}

#' @title Assemble python env info for withr
#' @export
python_env <- function() {
  config  <- get_project_config()
  envvar <- c("RETICULATE_PYTHON" = config$python_path)
  return(envvar)
}

