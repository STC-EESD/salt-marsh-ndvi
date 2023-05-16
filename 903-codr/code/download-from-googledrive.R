
download.from.googledrive <- function(
    google.drive.folder = "earthengine",
    destination.folder  = "multiyear_sample_gee_output"
    ) {

    thisFunctionName <- "download.from.googledrive";
    cat("\n### ~~~~~~~~~~~~~~~~~~~~ ###");
    cat(paste0("\n",thisFunctionName,"() starts.\n\n"));

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    options(
        gargle_oauth_email = Sys.getenv("GARGLE_OAUTH_EMAIL"),
        gargle_oauth_cache = Sys.getenv("GARGLE_OAUTH_CACHE")
        );

    require(googledrive);

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    DF.drive <- as.data.frame(googledrive::drive_find());

    saveRDS(
        object = DF.drive,
        file   = "DF-google-drive.RData"
        );

    # cat("\nstr(DF.drive)\n");
    # print( str(DF.drive)   );

    cat("\nDF.drive[,c('name','id')]\n");
    print( DF.drive[,c('name','id')]   );

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    row.index <- which(DF.drive[,'name'] == google.drive.folder);
    google.drive.ID <- DF.drive[row.index[1],'id'];

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    DF.earth.engine <- as.data.frame(googledrive::drive_ls(
        path    = googledrive::as_id(google.drive.ID),
        pattern = "^saltmarsh.+\\.csv$"
        ));

    saveRDS(
        object = DF.earth.engine,
        file   = "DF-Drive-ls-folder.RData"
        );

    cat("\nDF.earth.engine\n");
    print( DF.earth.engine   );

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    original.folder <- base::getwd();
    target.folder   <- base::file.path(original.folder,destination.folder);
    if ( !base::dir.exists(target.folder) ) {
        dir.create(
            path      = target.folder,
            recursive = TRUE
            );
        }
    base::setwd(dir = target.folder);

    for ( temp.id in DF.earth.engine[,'id'] ) {
        cat("\ndownloading:",temp.id,"\n");
        googledrive::drive_download(file = googledrive::as_id(temp.id));
        }

    base::setwd(dir = original.folder);

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    cat(paste0("\n",thisFunctionName,"() quits."));
    cat("\n### ~~~~~~~~~~~~~~~~~~~~ ###\n");
    return( NULL );

    }

##################################################
