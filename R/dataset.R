# Functions to interact with  datasets.

#'@title Create a \code{tar_target} for using a dataset from \code{datasets/}
#' @param dataset  A string or symbol.
#' @export
use_dataset <- function(dataset) {
  dataset <- targets::tar_deparse_language(substitute(dataset))
  withr::with_envvar(
    new = python_env(), {
    fluke_datasets <- reticulate::import("fluke.config.datasets")
    datasets <- fluke_datasets$Datasets()
    tar_cmd <- datasets[dataset]$tar_cmd()

    # return tar_cmd evaluated
    return(eval(parse(text = tar_cmd)))
  })
}
