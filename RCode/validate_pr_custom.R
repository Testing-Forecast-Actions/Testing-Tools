#!/usr/bin/env Rscript


get_script_path <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) > 0) {
    return(normalizePath(sub("^--file=", "", file_arg)))
  } else {
    stop("Impossibile determinare il percorso dello script.")
  }
}
script_dir <- dirname(get_script_path())
source(file.path(script_dir, "validate_model_output_chunked.R"))


# source("./validate_model_output_chunked.R")

suppressPackageStartupMessages({
  library(optparse)
  library(hubValidations)
})

# --- Function to classify PR changes 
classify_changed_files <- function(files) {
  files <- files[files != ""]

  model_files <- files[grepl("^model-output/.*\\.parquet$", files)]
  metadata_files <- files[grepl("^model-metadata/.*\\.ya?ml$", files)]
  invalid_files <- setdiff(files, c(model_files, metadata_files))

  list(
    model_files = model_files,
    metadata_files = metadata_files,
    invalid_files = invalid_files
  )
}

# -- Extract team_id from path model-output/team-model/file.parquet
extract_team_id <- function(file_path) {
  parts <- strsplit(file_path, "/")[[1]]
  idx <- which(parts == "forecast-models")
  parts[idx + 1]
}

main <- function() {
  option_list <- list(
    make_option("--hub_path", type = "character", help = "Root path for the repo hub"),
    make_option("--all_changed_files", type = "character", help = "Comma separated list of all the changes in the PR"),
    make_option("--check_submit_window", type = "logical", default = TRUE, help = "Check submission window")
  )

  opt <- parse_args(OptionParser(option_list = option_list))
  changed_files <- unlist(strsplit(opt$all_changed_files, ","))

  message("=== Starting PR custom validations ===")

  # 1. Check hub configuration
  cfg_check <- hubValidations::new_hub_validations()
  cfg_check$valid_config <- hubValidations::try_check(
    hubValidations::check_config_hub_valid(opt$hub_path),
    file_path = NULL
  )
  
  if (hubValidations::not_pass(cfg_check$valid_config)) {
    # hubValidations::print_validations(cfg_check)
    stop("❌ Invalid hub configuration detected")
  }

  # 2. Check for submission window
  if (opt$check_submit_window) {

    submit_window_ref_date_from = c(
      "file",
      "file_path"
    )
    
    checks_submission_time <-hubValidations::validate_submission_time(
      hub_path = opt$hub_path,
      file_path = changed_files,
      ref_date_from = submit_window_ref_date_from
    )

    has_errors <- !hubValidations::check_for_errors(checks_submission_time)
    if (has_errors) {
      hubValidations::print_validations(checks_submission_time)
      stop("❌ Submission failed: One or more files were submitted outside the allowed window.")
    }
  }

  # 3. Classify changes in the PR for further validations
  files <- classify_changed_files(changed_files)
  message("📦 Lista dei files classificati:")
  str(files)

  if (length(files$invalid_files) > 0) {
    msg <- paste0(
      "Invalid files found in the PR:\n",
      paste(" -", files$invalid_files, collapse = "\n")
    )
    err <- hubValidations::new_hub_validations()
    err$metadata_exists <- hubValidations::try_check(
      stop(msg),
      file_path = NULL
    )
    
    # err$invalid_files <- hubValidations::validation_error(
    #   msg,
    #   check_name = "invalid_files_in_pr"
    # )
    # hubValidations::print_validations(err)
    stop("❌ PR rejected: Invalid files are present.")
  }

  validation_results <- list()

  # 4. Validate meta-data
  for (meta_file in files$metadata_files) {
    message("→ Validating metadata: ", meta_file)
    res <- hubValidations::validate_model_metadata(
      hub_path = opt$hub_path,
      file_path = meta_file
    )
    validation_results <- c(validation_results, list(res))
  }

  # 5. Validate model output (with chunks)
  for (model_file in files$model_files) {
    message("→ Validating model output: ", model_file)

    team_id <- extract_team_id(model_file)
    metadata_path_yaml <- file.path(opt$hub_path, "model-metadata", paste0(team_id, ".yaml"))
    metadata_path_yml  <- file.path(opt$hub_path, "model-metadata", paste0(team_id, ".yml"))

    if (!file.exists(metadata_path_yaml) && !file.exists(metadata_path_yml)) {
      err <- hubValidations::new_hub_validations()
      err$metadata_exists <- hubValidations::try_check(
        stop("Metadata file missing for model-output file: ", team_id),
        file_path = model_file
      )

      # err <- hubValidations::new_hub_validations()
      # err$metadata_exists <- hubValidations::validation_error(
      #   paste("Metadata file missing for model-output file:", team_id),
      #   check_name = "metadata_exists",
      #   file = model_file
      # )
      validation_results <- c(validation_results, list(err))
      next
    }

    is_valid <- validate_model_output_chunked(
      file_path = model_file,
      hub_path = opt$hub_path,
      split_column = "location",
      rows_per_chunk = 500000,
      output_dir = "chunks",
      log_file = paste0("validation_", gsub("/", "_", model_file), ".log")
    )
    if (!is_valid) {
      err <- hubValidations::new_hub_validations()

      err$metadata_exists <- hubValidations::try_check(
        stop("Error validating file:", model_file),
        file_path = model_file
      )
      
      # err$validation_error <- hubValidations::validation_error(
      #   paste("Error validating file:", model_file),
      #   check_name = "model_output_validation",
      #   file = model_file
      # )
      validation_results <- c(validation_results, list(err))
    }    
  }

  # 6. Aggregate results
  combined <- do.call(hubValidations::combine_validations, validation_results)
  # hubValidations::print_validations(combined)
  hubValidations::check_for_errors(combined)
  message("✅ Validations completed successfully.")
}

main()
