
#' @title From a list of targets, filter specific targets
#' and get target names
#' @param targets_list A list of targets
#' @param names return names instead?
#' @param regexp Regular expression to filter list of targets.
#' @export
get_targets <- function(targets_list, regexp = NULL, names = FALSE) {
  targets::tar_assert_target_list(targets_list)
  tar_list_unlist <- unlist(targets_list)
  .names <- sapply(tar_list_unlist, function(x) x$settings$name)
  bools <- !vector(length = length(tar_list_unlist))
   if (!is.null(regexp)) {
     bools <- stringr::str_detect(.names, regexp)
   }
   if (!names) {
     return(tar_list_unlist[bools])
   } else {
     return(.names[bools])
   }
}