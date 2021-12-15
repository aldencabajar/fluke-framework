TEST_PROJECT_NAME=test-project
.PHONY: r_pkg_install

test_dir:
	sherpa create --pid test-bq-project-332617 --dataset test_dataset $(TEST_PROJECT_NAME)

clean_test:
	rm -rf  $(TEST_PROJECT_NAME)

test_deps:
	cd $(TEST_PROJECT_NAME);Rscript -e "renv::install('devtools')"

r_pkg_install:
	cd $(TEST_PROJECT_NAME); Rscript -e "devtools::install('../', quick = TRUE)"

