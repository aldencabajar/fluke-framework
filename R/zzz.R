
fluke_datasets <- NULL

.onLoad <- function(libname, pkgname) {
  # import python module
  # tryCatch({
  #   config  <- get_project_config()
  #   envvar <- c("RETICULATE_PYTHON" = config$python_path)
  #   withr::with_envvar(
  #     new = envvar, {
  #     fluke_datasets <<- reticulate::import("fluke.config.datasets", delay_load = TRUE)
  #   })
  # },
  # error = function(e) {
  #   cat("Are you inside a fluke project? Consider changing directory.\n")
  # })

}