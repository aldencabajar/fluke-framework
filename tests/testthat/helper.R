
PROJECT_NAME <- "my-test-project"
PKG_NAME <- "my_test_project"
TEST_DIR <- "~/test-fluke-pkg"


local_project_dir <- function(dir = tempfile(), env = parent.frame()) {
  old_dir <- getwd()
  fs::dir_create(dir)
  setwd(dir)
  local({
    # set renv global package cache
    Sys.setenv(RENV_PATHS_ROOT = "~/.cache/R/renv")
    proj <- init_fluke_project(PROJECT_NAME, PKG_NAME)

    #change working directory to project path
    setwd(proj)

  })

  withr::defer({
    setwd(old_dir)
    fs::dir_delete(dir)
  }, envir = env
  )

}

init_fluke_project <- function(project_name, pkg_name, path = getwd()) {
  args <- c(
    "create", "--path",
    path, "--pkg_name",
    pkg_name, project_name
  )
  system2("fluke", args)

  return(file.path(path, project_name))
}

csv_dataset <- function(dataset, name, env = parent.frame()) {

  path_to_ds <- file.path(getwd(), "datasets", paste0(dataset, ".csv"))
  path_to_config <- file.path(getwd(), "config", "datasets.yaml")
  df <- eval(rlang::sym(dataset))
  write.csv(df, path_to_ds)
  yaml_payload <- list(
    datasets = list(
        list(
        type = "csv",
        params = list(
          location = file.path("datasets", basename(path_to_ds)),
          read_fun = "read.csv"
        )
      )
    )
  )
  names(yaml_payload$datasets) <- name

  yaml::write_yaml(yaml_payload, file = path_to_config)
  withr::defer({
    fs::file_delete(path_to_ds)
    fs::file_delete(path_to_config)
  }, envir = env)

  return(path_to_ds)
}





