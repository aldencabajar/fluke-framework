source(here::here("tests", "testthat", "helper.R"))
library(testthat)

testthat::test_that("`use_dataset` works as expected.", {
  local_project_dir()
  path_to_ds <- csv_dataset("iris", "iris_data")

  renv::load()
  trg <- fluke::use_dataset(iris_data, path_only = FALSE)
  expect_true(
    all(sapply(targets::tar_assert_target_list(trg), is.null))
  )

})

testthat::test_that("`read_dataset` works as expected.", {
  local_project_dir()
  path_to_ds <- csv_dataset("iris", "iris_data")

  renv::load()

  # formulate targets and create tar script
  targets::tar_script(
    targs <- list(
      fluke::use_dataset(iris_data, path_only = FALSE),
      targets::tar_target(read_data_object, fluke::read_dataset(iris_data_path))
    )
  )

  # run pipeline
  targets::tar_make()
  expect_success(expect_target_exists(read_data_object))
  # print(fs::dir_ls("_targets/"))

  # path to dataset object inside `_targets` dir.
  # ds_path_in_tar <- file.path("_targets", "objects")
  # expect_true(fs::file_exists())


})

