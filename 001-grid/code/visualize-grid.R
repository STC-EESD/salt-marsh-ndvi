
visualize.grid <- function(
    SF.canada = NULL
    ) {

    thisFunctionName <- "visualize.grid";

    cat("\n### ~~~~~~~~~~~~~~~~~~~~ ###");
    cat(paste0("\n# ",thisFunctionName,"() starts.\n"));

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    visualize.grid_inner(
        SF.canada = SF.canada
        )

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    cat(paste0("\n# ",thisFunctionName,"() exits."));
    cat("\n### ~~~~~~~~~~~~~~~~~~~~ ###\n");
    return( NULL );

    }

##################################################
visualize.grid_inner <- function(
    SF.canada = NULL
    ) {

    my.tmap <- tmap::tm_shape(SF.canada) + tmap::tm_borders();
    # my.tmap <- my.tmap + tmap::tm_shape(SF.year) + tmap::tm_dots( # tmap::tm_bubbles(
    #     size  = err.colname, # "NDVI.err.codr.230m", # "area",
    #     col   = "orange",
    #     alpha = 0.5
    #     );
    my.tmap <- my.tmap + tmap::tm_layout(
        legend.position   = c("right","bottom"),
        legend.title.size = 1.0,
        legend.text.size  = 0.8
        );

    PNG.output <- paste0("plot-grid.png");
    tmap::tmap_save(
        tm       = my.tmap,
        filename = PNG.output,
        width    = 16,
        # height =  8,
        units    = "in",
        dpi      = 300
        );

    return( NULL );

    }
