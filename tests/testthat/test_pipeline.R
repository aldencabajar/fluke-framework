# Test functions for pipelines

## declare fixtures
local_project_dir()
version_name <- "test"
store_path <- file.path("pipelines", "store")

## Tests
test_that("all pipelines run with a single `tar_make` call.", {
  set_pipelines_config(
    list(pipelines = list(version = "test"))
  )
  # create two pipelines
  create_pipeline("foo")
  create_pipeline("bar")

  # write targets within each pipeline
  write_to_pipeline_script("foo", {
    list(
      tar_target(data1, data.frame(a = c(1, 2), b = c(3, 4))),
      tar_target(proc, data1$a + 1)
    )
  })

  write_to_pipeline_script("bar", {
    list(tar_target(proc2, proc + 1))
  })
  # setup environment
  fluke::setup_pipelines()
  fluke::install()
  # run `tar_make`
  targets::tar_make()
  expect_success(expect_dir_exists(file.path(store_path, version_name)))
  withr::defer({
    fs::dir_delete(
      file.path(store_path, version_name)
    )
  })
})



test_that("params for a specific pipeline can be
used when defined in pipeline.yaml.", {
  config <- list(
    pipelines = list(version = "test"),
    data_process = list(a = 1, b = 2)
  )
  set_pipelines_config(config)
  create_pipeline("data_process")
  write_to_pipeline_script("data_process", {
    list(
      tar_target(data1, data.frame(d = c(1, 2))),
      tar_target(proc, data1$d + data_process$a)
    )
  })

  fluke::setup_pipelines()
  fluke::install()
  targets::tar_make()

  expect_success(expect_dir_exists(file.path(store_path, version_name)))
  withr::defer({
    fs::dir_delete(
      file.path(store_path, version_name)
    )
  })

})