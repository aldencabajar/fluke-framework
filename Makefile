TEST_PROJECT_NAME=test-project
TEST_PKG=test_package
.PHONY: r_pkg_install

test_dir:
	fluke create --pkg_name $(TEST_PKG) $(TEST_PROJECT_NAME)

clean_test:
	rm -rf  $(TEST_PROJECT_NAME)

r_pkg_install:
	cd $(TEST_PROJECT_NAME); Rscript -e "devtools::install('../', quick = TRUE)"

build_and_install:
	Rscript -e "devtools::document()"
	Rscript -e "devtools::install(quick=TRUE)"

# R UNIT TESTING
test_r_pkg:
	cd tests;Rscript -e "testthat::test_dir('testthat')"
