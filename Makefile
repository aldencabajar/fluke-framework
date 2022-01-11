TEST_PROJECT_NAME=test-project
Rscript=/usr/bin/Rscript
TEST_PKG=test_package
.PHONY: r_pkg_install
curr_wd := $(shell pwd)

$(info $$curr_wd = $(curr_wd))

dev-setup:
	$(Rscript) --vanilla -e  "source('renv/activate.R');renv::restore()"
	pip install -r requirements.txt

test-proj-create:
	fluke create --pkg_name $(TEST_PKG) $(TEST_PROJECT_NAME)

test-proj-clean:
	rm -rf  $(TEST_PROJECT_NAME)


# PACKAGE DEVELOPMENT
PKG_VERSION = 0.0.0.9000
build_path := $(curr_wd)/fluke/templates/project/{{cookiecutter.project_name}}/renv/local/
$(info BUILD=$(build))

build_pkg := $(build_path)/fluke_$(PKG_VERSION).tar.gz
.PHONY: build_pkg

$(build_pkg): $(shell find R -type f)
	$(Rscript) -e "devtools::document()"
	$(Rscript) -e "devtools::build(path='$(build_path)')"

r-pkg-install:
	cd $(TEST_PROJECT_NAME); Rscript -e "devtools::install('../', quick = TRUE)"


# R UNIT TESTING
test-r-pkg: $(build_pkg)
	$(Rscript) -e "testthat::test_dir('tests/testthat')"

## declare path to test file
test_file_path := $(curr_wd)/tests/testthat/test_$(file).R
$(info $$test_file = $(test_file_path))

test-file: $(build_pkg)
	$(Rscript) -e "testthat::test_file('$(test_file_path)')"

