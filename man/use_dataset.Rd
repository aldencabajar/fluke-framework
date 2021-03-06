% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/dataset.R
\name{use_dataset}
\alias{use_dataset}
\title{Create a \code{tar_target} for using a dataset from \code{datasets/}}
\usage{
use_dataset(dataset, path_only = TRUE)
}
\arguments{
\item{dataset}{A string or symbol.}

\item{path_only}{Only list path as target? FALSE would list a target that
would read the dataset from path.}
}
\value{
A list of targets with names \verb{<dataset>_path} and \verb{<dataset>}, respectively.
}
\description{
Create a \code{tar_target} for using a dataset from \code{datasets/}
}
