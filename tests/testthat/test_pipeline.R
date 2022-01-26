# Test functions for pipelines

## declare fixtures
local_project_dir()

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

  expect_dir_exists("pipelines/store/test")
})
