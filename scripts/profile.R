shhh <- suppressPackageStartupMessages

shhh(library(tidyverse))
shhh(library(magrittr))
shhh(library(glue))
shhh(library(feather))
filter <- dplyr::filter

readRenviron("../.env")

local({
    w_repos  <- getOption("repos")
    w_repos["CRAN"] <- "https://cran.itam.mx"
    options(repos = w_repos)
})

.env <- new.env()
.env$all_equal  <- function (x) all(x %in% x[1])

.env$not_na     <- function (x) not(is.na(x))

.env$not_in     <- function (x, y_set) not(x %in% y_set)

.env$not_exists <- function (a_file) not(file.exists(a_file))

.env$classes    <- function (a_df) tibble(
    name  = names(a_df),
    class = map_chr(a_df, ~(class(.x)[1])))

.env$quotemeta  <- function (x) str_replace_all(x, "(\\W)", "\\\\\\1")

.env$str_delatinize <- function (x) chartr("ÁÉÍÓÚÑáéíóúñ", "AEIOUÑaeiouñ", x)
attach(.env)


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


## Configuration



## Functions

# Para todas las sesiones




# Menos útiles

list_w_nulls_2_chr <- function (xx) {
  # Double xx and yy to avoid confusion with argument .x,
  # which is defined implicitely in ~(f(.x)) notation.
  yy <- map_chr(xx,
    .f = ~(if (is.null(.x)) "" else as.character(.x) ))
  return (yy)
}

k_occurrence <- function (x, dups_only=TRUE) {
  # Integer vector of the occurrence of each value of X.
  # When DUPS_ONLY = TRUE, the non-duplicated values become 0.
  x_tbl <- table(x)
  if (dups_only) {x_tbl <- x_tbl[x_tbl > 1]}
  y <- rep(0, length(x))
  for (x_0 in names(x_tbl)) {y[x == x_0] <- 1:x_tbl[x_0]}
  return (y)
}

str_as_key <- function (x, sep="-", dups_only=TRUE) {
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
  if (length(modes) == 1) {modes <- rep(modes, length(cols))}

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
  } else {
    warning (".gitignore exists in dir: %s" %>% sprintf(the_dir))
  }
  lines_for_file <- c("*", "!.gitignore")
  writeLines(lines_for_file, ignore_file)
}




