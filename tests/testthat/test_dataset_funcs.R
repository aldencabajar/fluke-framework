
testthat::test_that("`use_dataset` works as expected.", {

  local_project_dir()
  path_to_ds <- csv_dataset("iris", "iris_data")

  require("fluke")
  trg <- use_dataset(iris_data, path_only = FALSE)
  expect_true(
    all(sapply(targets::tar_assert_target_list(trg), is.null))
  )

})

testthat::test_that("`read_dataset` works as expected.", {

  local_project_dir()
  path_to_ds <- csv_dataset("iris", "iris_data")

  local({
    require("fluke")

    # formulate targets
    targs <- list(
      use_dataset(iris_data, path_only = FALSE),
      tar_target(read_data_object, read_dataset(iris_data_path))
    )

  })

})

