#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(optparse)
  library(arrow)
  library(dplyr)
  library(hubValidations)
  library(purrr)
})

# === ARGOMENTI CLI ===
option_list <- list(
  make_option(c("-i", "--input"), type = "character", help = "Percorso al file .parquet (dentro hub_path!)"),
  make_option(c("-u", "--hub"), type = "character", help = "Cartella con tasks.json (root dell'hub)"),
  make_option(c("-s", "--split"), type = "character", default = NULL, help = "Colonna per dividere (es. 'location')"),
  make_option(c("-r", "--rows"), type = "integer", default = 500000, help = "Righe per chunk (se split è NULL)"),
  make_option(c("-o", "--out"), type = "character", default = "chunks", help = "Cartella di output"),
  make_option(c("-l", "--log"), type = "character", default = "validation_errors.log", help = "File log errori")
)
opt <- parse_args(OptionParser(option_list = option_list))

# === CONFIG ===
# path to the parquet file relative to hub_path/model-output/
parquet_path <- opt$input
# hub root folder 
hub_path <- opt$hub
split_column <- opt$split
rows_per_chunk <- opt$rows
output_dir <- opt$out
logfile <- opt$log

dir.create(output_dir, showWarnings = FALSE)
if (file.exists(logfile)) file.remove(logfile)

  log_error <- function(message) {
  cat(message, "\n", file = logfile, append = TRUE)
}



# === BACKUP ORIGINAL FILE ===
input_src_absolute = file.path(hub_path, "model-output", parquet_path)
src_file_name <- basename(input_src_absolute)
src_full_path <- normalizePath(input_src_absolute)
backup_path <- file.path(output_dir, paste0("backup_", src_file_name))

cat("📁 Backup del file sorgente in:", backup_path, "\n")
file.copy(src_full_path, backup_path, overwrite = TRUE)



# --- helper: sanitizza e garantisce l'esclusione di administered_doses post-collect
sanitize_and_exclude_admin <- function(df) {
  if (!"target" %in% names(df)) return(df)
  df$target <- if (is.factor(df$target)) as.character(df$target) else df$target
  df$target <- tolower(trimws(df$target))
  n_before <- nrow(df)
  df2 <- df[is.na(df$target) || df$target != "administered_doses", , drop = FALSE]
  n_removed <- n_before - nrow(df2)
  if (n_removed > 0) {
    log_append(sprintf("[post-collect] rimossi %d record con target administered_doses residui dopo sanitizzazione", n_removed))
  }
  df2
}




# --- Validate chunk function 
# ------------------------------------------------------
validate_chunk <- function(fpath, fname) {
  # Sovrascrivi il sorgente nel path originale (requisito del pacchetto)
  file.copy(fpath, src_full_path, overwrite = TRUE)
  cat("📦 Validating model file:", fname, "\n")

  res_file <- hubValidations::validate_model_file(hub_path = hub_path, file_path = parquet_path)

  if (any(purrr::map_lgl(res_file, ~ is_any_error(.x)))){
    cat("❌ INVALID MODEL FILE:", fname, "\n")
    log_append(paste0("INVALID MODEL FILE: ", fname))
    return (FALSE)
  }

  cat("📦 Validating model data...\n")
  res <- hubValidations::validate_model_data(hub_path = hub_path, file_path = parquet_path)

  # TRUE = no errors; FALSE = there is some error
  if (!hubValidations:::check_for_errors(res)) {
    cat("❌ INVALID FILE:", fname, "\n")
    log_append(paste0("INVALID: ", fname))
    capture.output(print(res$errors)) |> walk(log_append)
    if (!is.null(res$missing)) {
      log_append("⚠️ Missing:")
      capture.output(str(res$missing, max.level = 2)) |> walk(log_append)
    }
    log_append("----")
    return(FALSE)
  } else {
    cat("✅ VALID FILE:", fname, "\n\n")
    return(TRUE)
  }
}


# === CARICAMENTO ===
# ds <- open_dataset(src_full_path)
ds <- open_dataset(backup_path)


# === TRACCIAMENTO STATI ===
valid_chunks <- c()
invalid_chunks <- c()


# === VALIDAZIONE 

# === SPLIT PER COLONNA (es. location) ===
if (!is.null(split_column)) {

  # First chunk is for administered_doses"
  cols_available <- names(ds)

  has_target <- "target" %in% cols_available
  if (has_target) 
  {
    # 1) Chunk "administered_doses" (if at least one row exists)
    #ds_adm <- open_dataset(backup_path) %>% filter(target == "administered_doses")
    ds_adm <- ds %>% filter(target == "administered_doses")
    n_adm  <- tryCatch({
      ds_adm %>% summarize(n = n()) %>% collect() %>% pull(n)
    }, error = function(e) 0L)

    # if the object is not NA n_adm has at least one record
    if (!is.na(n_adm) && n_adm > 0) 
    {
      df_adm <- ds_adm %>% collect()

      # write the parquet file to output dir      
      fname_adm <- "chunk_administered_doses.parquet"
      fpath_adm <- file.path(output_dir, fname_adm)
      write_parquet(df_adm, fpath_adm)
      

      # call the validation function 
      ok <- validate_chunk(fpath_adm, fname_adm)
      if (ok) valid_chunks <- c(valid_chunks, fname_adm) else invalid_chunks <- c(invalid_chunks, fname_adm)
      
      rm(df_adm); invisible(gc())
    
    } else {
      cat("ℹ️  Nessun record con target == 'administered_doses'. Salto il primo chunk.\n")
    }


    # 2) Validate remaining chunks by split_column, excluding administered_doses
    cat("Filtering groups...\n")
    group_values  <- ds %>%
      filter( target != "administered_doses" | is.na(target)) %>%
      distinct(.data[[split_column]]) %>% collect() %>% pull()

    for (group_value in group_values ) {
      
      cat("Iterating over groups...\n")

      df <- ds %>% 
          filter(.data[[split_column]] == group_value &
                    (!(target == "administered_doses") | is.na(target))) %>% 
          collect()

      # doppio check in R dopo collect (robusto a spazi/case)
      cat("sanitizing...\n")
      # df <- sanitize_and_exclude_admin(df)
      
      if ("target" %in% names(df)) {
        n_admin_left <- sum(!is.na(df$target) & df$target == "administered_doses")
        if (n_admin_left > 0) {
          log_append(sprintf("[safety] trovati %d administered_doses nel chunk %s dopo filtro; li rimuovo.", n_admin_left, as.character(group_value)))
          df <- df[df$target != "administered_doses" | is.na(df$target), , drop = FALSE]
        }
      }

      fname <- paste0("chunk_", split_column, "=", group_value, ".parquet")
      fpath <- file.path(output_dir, fname)
      write_parquet(df, fpath)

      ok <- validate_chunk(fpath, fname)
      if (ok) valid_chunks <- c(valid_chunks, fname) else invalid_chunks <- c(invalid_chunks, fname)

      rm(df); invisible(gc())
    }

  } else {   # has_target
     # Se non c'è la colonna target, fallback: normale split per colonna
    cat("⚠️  Column 'target' not found: proceed with standard split for ", split_column, "\n")
  }

} else {
  # === SPLIT PER BLOCCHI DI RIGHE ===
  total_rows <- ds %>%
    summarize(n = n()) %>%
    collect() %>%
    pull(n)

  steps <- ceiling(total_rows / rows_per_chunk)

  for (i in 0:(steps - 1)) {
    start_row <- i * rows_per_chunk + 1
    end_row <- min((i + 1) * rows_per_chunk, total_rows)

    df <- ds %>%
      slice(start_row:end_row) %>%
      collect()

    fname <- paste0("chunk_", i + 1, ".parquet")
    fpath <- file.path(output_dir, fname)

    write_parquet(df, fpath)

    ok <- validate_chunk(fpath, fname)
    if (ok) valid_chunks <- c(valid_chunks, fname) else invalid_chunks <- c(invalid_chunks, fname) 

    rm(df); invisible(gc())
  }
} # else split column


# === RIPRISTINO DEL FILE ORIGINALE ===
cat("♻️  Ripristino del file originale in:", src_full_path, "\n")
file.copy(backup_path, src_full_path, overwrite = TRUE)

# === RIEPILOGO ===
cat("\n📊 RIEPILOGO VALIDAZIONI\n")
cat("✅ Chunk validi:", length(valid_chunks), "\n")
cat("❌ Chunk invalidi:", length(invalid_chunks), "\n")

if (length(invalid_chunks) > 0) {
  cat("📄 Dettagli in:", logfile, "\n")
}
