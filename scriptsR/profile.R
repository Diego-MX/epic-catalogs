shhh <- suppressPackageStartupMessages

shhh(library(tidyverse))
shhh(library(magrittr))
shhh(library(glue))
shhh(library(feather))
filter <- dplyr::filter

readRenviron("../.env")



all_equal <- function (x) all(x %in% x[1])

not_exists <- function (file) not(file.exists(file))

not_in <- function (x, y_set) not(x %in% y_set)*1

not_na <- function (x) not(is.na(x))*1

quotemeta <- function (x) str_replace_all(x, "(\\W)", "\\\\\\1")

str_delatinize <- function (x) chartr("ÁÉÍÓÚÑáéíóúñ", "AEIOUÑaeiouñ", x)


classes <- function (a_df) {
  its_classes_df <- tibble(
      name = names(a_df), 
      class = map_chr(a_df, ~(class(.x)[1])) )
  return (its_classes_df)
}


list_w_nulls_2_chr <- function (xx) {
  # Double xx and yy to avoid confusion with argument .x, 
  # which is defined implicitely in ~(f(.x)) notation. 
  yy <- map_chr(xx, ~(if (is.null(.x)) "" else as.character(.x) ))
  return (yy)
}
 


k_occurrence <- function (x, dups_only=TRUE) {
  # Integer vector of the occurrence of each value of X. 
  # When DUPS_ONLY = TRUE, the non-duplicated values become 0.
  x_tbl <- table(x)
  if (dups_only) x_tbl <- x_tbl[x_tbl > 1] 
  
  y <- rep(0, length(x))
  for (x_0 in names(x_tbl)) { y[x == x_0] <- 1:x_tbl[x_0] }
  return (y)
}

str_as_key <- function (x, sep="-", dups_only=TRUE) {
  # Adds K_OCURRENCE of repetitions to make unique. 
  x_occur <- k_occurrence(x, dups_only)
  x_ext   <- if_else(x_occur > 0, str_c(sep, x_occur), "")
  
  y <- str_c(x, x_ext) 
  return (y)
} 

str_codify <- function (x) {
  y <- x %>% str_delatinize() %>% 
    str_to_lower() %>% 
    str_replace_all(" ", "-")
  return (y)
}

tbl_empty <- function (cols, modes) {
  if (length(modes) == 1) modes <- rep(modes, length(cols))
  
  cols_list <- map(modes, ~vector(.x, 0)) %>% set_names(cols)
  the_tbl   <- tibble(!!!cols_list)  
  return (the_tbl)
}

setup_data_dir <- function (the_dir) {
  if (the_dir %>% not_exists()) {
    dir.create(the_dir)
    gitignore_contents(the_dir)
    
    dir.create(the_dir %>% file.path("cache"))
  }
}

gitignore_contents <- function (the_dir) {
  ignore_file <- file.path(the_dir, ".gitignore")
  if (ignore_file %>% not_exists()) {
    file.create(ignore_file)
    lines_for_file <- c("*", "!.gitignore")
    writeLines(lines_for_file, ignore_file)  
  } else {
    warning (".gitignore exists in dir: %s" %>% sprintf(the_dir))
  }
}


## Fun stuff 

if (interactive()) {
  fortunes::fortune()
} else {
  options(readr.num_columns=0)
}

