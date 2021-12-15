
migrate_bigquery <- function(table, dataset, project) {
  bq_tbl <- bigrquery::bq_table(
    project = project,
    dataset = dataset,
    table = table
  )
  bigrquery::bq_table_download(bq_tbl)

}

migrate_run_wrapper <- function(dataset_dir, migrate_fn, table, ...) {
  args <- list(...)
  tbl <- do.call(migrate_fn, list(table = table, ...))
  path_to_tbl_rds <- file.path(
    rprojroot::find_rstudio_root_file(),
    "datasets",
    dataset_dir,
    paste0(table, ".rds")
  )
  saveRDS(tbl, path_to_tbl_rds)

}

# create_sherpa_dataset <- function(version_dir, migrate_fn, tables, ...) {
#   trgs <- lapply(
#     tables,
#       function(tbl) {
#         args <- list(...)
#         cmd <- as.call(
#           c(list(
#             substitute(func, env = list(func = as.symbol(migrate_fn))),
#             table = tbl
#           ),
#           as.list(substitute(args)))
#         )
#         print(cmd)
#         targets::tar_target_raw(tbl, cmd)
#       }
#   )
#   return(trgs)
# }

# create_sherpa_dataset("temp", "load_bq", c("template","table"),
# db = "foo", pid = "bar")
