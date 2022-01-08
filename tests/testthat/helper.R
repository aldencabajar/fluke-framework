PROJECT_NAME <- "my-test-project"
PKG_NAME <- "testproj"
TEST_DIR <- "~/test-fluke-pkg"


local_project_dir <- function(dir = tempfile(), env = parent.frame()) {
  old_dir <- getwd()
  old_envvars <- Sys.getenv()
  fs::dir_create(dir)
  setwd(dir)
  withr::with_envvar(
    c(RENV_PATHS_ROOT = "~/.cache/R/renv"), {
    proj <- init_fluke_project(PROJECT_NAME, PKG_NAME)
    #change working directory to project path
    setwd(proj)
  })

  renv::load()

  withr::defer({
    revert_envvars(old_envvars)
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

  # formulate the yaml payload
  yaml_payload <- list(
    datasets = list(
        list(
        type = "csv",
        params = list(
          location = basename(path_to_ds),
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


#'@title reverts environment variables to a previous state
revert_envvars <- function(old_envvar) {
  # detect envvars not in original envvar
  old_env_names <- names(old_envvar)
  new_env_names <- names(Sys.getenv())
  var_missing <- new_env_names[!new_env_names %in% old_env_names]
  Sys.unsetenv(var_missing)
}

expect_target_exists <- function(target_name) {
  tar_quo <- rlang::enquo(target_name)
  act <- quasi_label(tar_quo, arg = "target_name")

  path_to_object <- file.path(
    targets::tar_config_get("store"),
    "objects",
    rlang::quo_name(tar_quo)
  )

  expect(
    fs::file_exists(path_to_object),
    sprintf("%s does not exists in `targets` store.", act$lab)
  )

  # 3. Invisibly return the value
  invisible(act$val)
}



