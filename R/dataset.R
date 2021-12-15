#'@description Reads the project configuration
get_project_config <- function() {
  # config file is at the same level as .Rproj
  proj_root <- rprojroot::find_rstudio_root_file()
  config <- yaml::yaml.load_file(file.path(proj_root, "sherpa-config.json"))
  return(config)
}


#'@title Use a migrated table within a dataset from \code{datasets/} directory.
#' @description
#' @param dataset STRING. Specifies the name of the dataset.
#' @param table STRING. specifies the migrated table.
#'@export
read_table_from_dataset <- function(dataset, table) {
  cfg <- get_project_config()
  ds_name_match <- lapply(cfg$datasets, function(x) dataset == x$name)

  if (all(!ds_name_match)) {
    stop(glue::glue("No dataset named `{name}`.
     Check datasets available using `sherpa datasets --list`"))
  }
  # get table and version
  dataset_idx <- which(ds_name_match)
  tbl_vers <- cfg$datasets[[dataset_idx]]$table_versions
  tbl_ver <- paste(table, tbl_vers[[table]], sep = "_")

  # get path to data file
  path_to_file <- here::here("datasets", dataset, tbl_ver)

  readRDS(path_to_file)

}