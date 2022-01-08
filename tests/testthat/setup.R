local({
# use libs in fluke-framework dir
  # libs <- file.path(
  #   dirname(dirname(getwd())),
  #   "renv/library/R-3.6/x86_64-pc-linux-gnu"
  #   )
  # .libPaths(libs)
  # print(.libPaths())

# unset RENV environment variables
vars <- names(Sys.getenv())
Sys.unsetenv(grep("^RENV", vars, value = TRUE))
})