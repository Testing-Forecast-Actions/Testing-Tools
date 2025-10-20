# main orchestrator file for custom validations
main <- function() {
  opt <- parse_args()  # usa optparse

  # 1. Check config hub (una volta)
  check_hub_config(opt$hub_path)

  # 2. Check finestra di submission (una volta, opzionale)
  if (opt$check_submit_window) {
    check_submission_window(opt$hub_path)
  }

  # 3. Prepara liste file
  model_files <- unlist(strsplit(opt$model_output_files, ","))
  metadata_files <- unlist(strsplit(opt$metadata_files, ","))

  validation_results <- list()

  # 4. Validazione METADATA files (eventuali)
  for (meta_file in metadata_files) {
    res <- hubValidations::validate_model_metadata(
      hub_path = opt$hub_path,
      file_path = meta_file
    )
    validation_results <- c(validation_results, list(res))
  }

  # 5. Validazione MODEL OUTPUT files (chunked)
  for (model_file in model_files) {
    # Estraggo team_id da path per cercare il metadata corrispondente
    team_id <- extract_team_id(model_file)

    metadata_path <- file.path(opt$hub_path, "model-metadata", paste0(team_id, ".yaml"))
    if (!file.exists(metadata_path)) {
      # Errore: metadata mancante per modello
      err <- hubValidations::new_hub_validations()
      err$metadata_exists <- hubValidations::validation_error(
        paste("Metadata mancante per modello:", team_id),
        check_name = "metadata_exists",
        file = model_file
      )
      validation_results <- c(validation_results, list(err))
      next
    }

    # Validazione con splitting
    res <- validate_model_output_chunked(
      file_path = model_file,
      hub_path = opt$hub_path,
      derived_task_ids = opt$derived_task_ids
    )
    validation_results <- c(validation_results, list(res))
  }

  # 6. Aggregazione + errore finale
  combined <- do.call(hubValidations::combine_validations, validation_results)
  hubValidations::check_for_errors(combined)
}
