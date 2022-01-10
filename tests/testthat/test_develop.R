# Test functions for package development under fluke.

## declare fixtures
local_project_dir()

# remove the package dir
fs::dir_delete(fluke::get_pkg_file_path())

func_script <- "
#' @title A dummy function
#' @description A dummy function
#' @export
test_func <- function(foo) {
  return(foo)
}
"

## TESTS
test_that("package is installed successfully inside fluke project.",  {
  local({
    pkg_skeleton()
    fluke::install()
    expect_true("fluke" %in% row.names(installed.packages()))
  })

})

test_that("fluke::document writes .Rd files within fluke proj package dir.", {
  local({
    pkg_skeleton()
    write_pkg_func(func_script, "foo.R")
    fluke::document()
    expect_success(expect_document_exists("test_func"))
  })
})

test_that("functions can be used after doing `fluke::update_package`.", {
  local({
    pkg_skeleton()
    write_pkg_func(func_script, "foo.R")
    fluke::update_package()
    library(testproj)
    expect_equal(test_func("foo"), "foo")
  })

})
