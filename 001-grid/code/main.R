
command.arguments <- commandArgs(trailingOnly = TRUE);
data.directory    <- normalizePath(command.arguments[1]);
code.directory    <- normalizePath(command.arguments[2]);
output.directory  <- normalizePath(command.arguments[3]);

print( data.directory );
print( code.directory );
print( output.directory );

print( format(Sys.time(),"%Y-%m-%d %T %Z") );

start.proc.time <- proc.time();

# set working directory to output directory
setwd( output.directory );

##################################################
require(cowplot);
require(dplyr);
require(ggplot2);
require(sf);
require(tidyr);
require(tmap);
require(units);

# source supporting R code
code.files <- c(
    "initializePlot.R",
    "visualize-grid.R"
    );

for ( code.file in code.files ) {
    source(file.path(code.directory,code.file));
    }

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
my.seed <- 7654321;
set.seed(my.seed);

is.macOS  <- grepl(x = sessionInfo()[['platform']], pattern = 'apple', ignore.case = TRUE);
n.cores   <- ifelse(test = is.macOS, yes = 2, no = parallel::detectCores() - 1);
cat(paste0("\n# n.cores = ",n.cores,"\n"));

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
data.snapshot.boundaries <- "2023-02-11.01";
SF.provinces.territories <- sf::st_read(
    dsn = file.path(data.directory,data.snapshot.boundaries,"lpr_000a21a_e","lpr_000a21a_e.shp")
    );
SF.provinces.territories$area  <- as.numeric(sf::st_area(sf::st_geometry(SF.provinces.territories))) / 1e6;
SF.provinces.territories$PRUID <- as.integer(SF.provinces.territories$PRUID);
cat("\nstr(SF.provinces.territories)\n");
print( str(SF.provinces.territories)   );

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
SF.canada <- sf::st_union(SF.provinces.territories);
cat("\nsf::st_crs(SF.canada)\n");
print( sf::st_crs(SF.canada)   );

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
visualize.grid(SF.canada = SF.canada);

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###

##################################################
print( warnings() );

print( getOption('repos') );

print( .libPaths() );

print( sessionInfo() );

print( format(Sys.time(),"%Y-%m-%d %T %Z") );

stop.proc.time <- proc.time();
print( stop.proc.time - start.proc.time );
