TEST_PROJECT_NAME=test-project
Rscript=/usr/bin/Rscript
TEST_PKG=test_package
.PHONY: r_pkg_install

dev-setup:
	$(Rscript) --vanilla -e  "renv::restore()"
	pip install -r requirements.txt

test_dir:
	fluke create --pkg_name $(TEST_PKG) $(TEST_PROJECT_NAME)

clean_test:
	rm -rf  $(TEST_PROJECT_NAME)

r_pkg_install:
	cd $(TEST_PROJECT_NAME); Rscript -e "devtools::install('../', quick = TRUE)"

document_and_build:
	$(Rscript) -e "devtools::document()"
	$(Rscript) -e "devtools::build(path='.')"

# R UNIT TESTING
test_r_pkg:
	$(Rscript) -e "testthat::test_dir('tests/testthat')"
