# Set of utility functions for database querying

# main function to run when querying
query_run_wrapper <- function(script, query_fn, ...) {
  # create new env and source it in env
  env <- new.env()
  out <- source(script, local = env)
  do.call(query_fn, list(output = out$value, ...))

}

# specific function for bigquery database
bigquery_query_fn <- function(output, ...) {
  opts <- list(...)
  print(opts)
  tbl <- bigrquery::bq_table(opts$project, opts$dataset, opts$table)
  bigrquery::bq_project_query(
    x = opts$project,
    query = output,
    destination_table = tbl,
    write_disposition = "WRITE_TRUNCATE"
  )
}
