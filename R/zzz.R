
fluke_datasets <- NULL

.onLoad <- function(libname, pkgname) {
  # import python module
  tryCatch({
    python_env({
      fluke_datasets <<- reticulate::import("fluke.config.datasets", delay_load = TRUE)
    })
  },
  error = function(e) {
    cat("Are you inside a fluke project? Consider changing directory.\n")
  })

}