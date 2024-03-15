

quotemeta  <- function (x) str_replace_all(x, "(\\W)", "\\\\\\1")


list_w_nulls_2_chr <- function (xx) {
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
    # Adds K_OCURRENCE of repetitions to make unique. 
    x_occur <- k_occurrence(x, dups_only)
    x_ext   <- if_else(x_occur > 0, str_c(sep, x_occur), "")
    y <- str_c(x, x_ext) 
    return (y)
} 


tbl_empty <- function (cols, modes) {
    if (length(modes) == 1) modes <- rep(modes, length(cols))
    cols_list <- map(modes, ~vector(.x, 0)) %>% set_names(cols)
    the_tbl   <- tibble(!!!cols_list)  
    return (the_tbl)
}
