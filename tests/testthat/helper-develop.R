#' @title writes a pacakge function with a fluke package
#' @param lines Stirng. lines of string to save.
#' @param file String. name of R script file
#' @param env Environment
write_pkg_func <- function(lines, file, env = parent.frame()) {
  pkg <- fluke::get_pkg_file_path()
  full_path <- file.path(pkg, "R", file)
  writeLines(lines, full_path)

  withr::defer(
    fs::file_delete(full_path),
    envir = env
  )
}

#' @title Test if a document exists within pkg
#' @param  func_name  String. Name of function.
expect_document_exists <- function(func_name) {
  doc_name <- paste0(func_name, ".Rd")
  doc_file_path <- file.path(
    fluke::get_pkg_file_path(),
    "man", doc_name
  )
  expect(
    fs::file_exists(doc_file_path),
    sprintf("%s does not exists in man/ inside the pkg dir", func_name)
  )
}

pkg_skeleton <- function(env = parent.frame()) {
  config <- fluke::get_project_config()
  DESCRIPTION <-  list(
    Package = config$pkg_name,
    Title = "What the Package Does",
    Version = "0.0.1",
    Description = "What the package does.",
    Encoding = "UTF-8",
    Roxygen = "list(markdown = TRUE)",
    RoxygenNote = "7.1.2"
  )


  pkg_path <- fluke::get_pkg_file_path()

  # create directories and files
  fs::dir_create(pkg_path)
  fs::dir_create(file.path(pkg_path, "R"))
  yaml::write_yaml(DESCRIPTION, file.path(pkg_path, "DESCRIPTION"))


  withr::defer({
    fs::dir_delete(pkg_path)
    renv::remove(config$pkg_name)

  },
    envir = env
  )
}


