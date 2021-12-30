# Convenience wrappers for handling package development related actions

#' @title Wrapper to devtools::install.
#' Installs the R package inside a fluke project.
#' @export
install <- function() {
  #get path to package and install
  devtools::install(get_pkg_file_path())

}

#' @title wrapper to devtools::document functions
#' with fluke project as context.
#' @export
document <- function() {
  # get path to package
  devtools::document(get_pkg_file_path())
}

#' @title Does both document() and install()
#' @export
update_package <- function() {
  devtools::document(get_pkg_file_path())
  devtools::install(get_pkg_file_path())
}

