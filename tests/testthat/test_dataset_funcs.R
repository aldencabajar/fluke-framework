library(testthat)
source(here::here("tests", "testthat", "helper.R"))
local_project_dir()
path_to_ds <- csv_dataset("iris", "iris_data")

testthat::test_that("`use_dataset` works as expected.", {

  trg <- fluke::use_dataset(iris_data, path_only = FALSE)
  expect_true(
    all(sapply(targets::tar_assert_target_list(trg), is.null))
  )

})

testthat::test_that("`read_dataset` works as expected.", {
  # local_project_dir()
  # path_to_ds <- csv_dataset("iris", "iris_data")

  # formulate targets and create tar script
  targets::tar_script(
    targs <- list(
      fluke::use_dataset(iris_data, path_only = FALSE),
      targets::tar_target(read_data_object, fluke::read_dataset(iris_data_path))
    )
  )

  # run pipeline
  local({
    targets::tar_make()
    expect_silent(targets::tar_load(read_data_object))
    expect_equal(read.csv(path_to_ds), read_data_object)
  })
})
