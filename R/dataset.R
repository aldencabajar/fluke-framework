# Functions to interact with  datasets.

#'@title Create a \code{tar_target} for using a dataset from \code{datasets/}
#' @param dataset  A string or symbol.
#' @param path_only Only list path as target? FALSE would list a target that
#' would read the dataset from path.
#' @return A list of targets with names `<dataset>_path` and `<dataset>`, respectively.
#' @export
use_dataset <- function(dataset, path_only = TRUE) {
  dataset <- targets::tar_deparse_language(substitute(dataset))

  python_env({

    datasets <- fluke_datasets$Datasets()
    ds_obj <- datasets[dataset]
    tar_list <- vector(mode = "list", length = 2L)
    loc <- as.character(ds_obj$params$location)
    read_fn <- as.character(ds_obj$params$read_fun)

    loc_tar <- dataset_path_target(dataset, loc)

    tar_list[[1]] <- loc_tar

    if (!path_only) {
      tar_list[[2]] <- eval(parse(text = ds_obj$tar_cmd()))
    }
    return(tar_list)

  })
}

dataset_path_target <- function(dataset, location) {
  targets::tar_target_raw(
    paste(dataset, "path", sep = "_"),
    substitute(path_,  env = list(path_ = location)),
    format = "file"
  )
}

#' @title read a dataset using params from config.
#' @param dataset_path String. Path to dataset.
#' @return A dataset object based on dataset type and \code{read_fun}.
#' @export
read_dataset <- function(path) {
  python_env({

      datasets <- fluke_datasets$Datasets()
      ds_obj <- datasets$get_dataset_by_loc(path)
      args <- list(
        path, unlist(ds_obj$params$read_fun_args)
      )
      # remove nulls
      args <- args[!sapply(args, is.null)]

      # run command
      do.call(ds_obj$params$read_fun, args)

  })
}

