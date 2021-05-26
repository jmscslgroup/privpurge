#!/bin/bash

cd /data/jmscslgroup/data_processing/scripts/privpurge
source ./logging.sh

log::make_print_func "log::dry_run"  "${log_fore_magenta}"   "${log_set_bold}"

usage() {
if [ -n "$1" ]; then log::error "$1"; fi
cat >&2 << EOF
usage: bash ${0} [-c CORES] [-d] [-v] [-h]
     -c CORES      provide the number of cores to run with [optional].
     -n            new run, run snakemake clean before snakemake (don't use with p) [optional].
     -p            pure run, run slakemake clean_all before snakemake (don't use with n) [optional].
     -d            dry run, just show what commands would be run [optional].
     -h            show help message and exit [optional].
EOF
exit 1
}

if [ $# -eq 0 ]; then usage; fi

while getopts :c:npdh flag
do
        case "${flag}" in
                 c) cores=${OPTARG};;
                 n) new_run=true;;
                 p) pure_run=true;;
                 d) dry_run=true;;
                 :) usage "missing argument for -$OPTARG";;
                \?) usage "unknown option: -$OPTARG";;
        esac
done
shift $((OPTIND-1))

run_id=$(date +"%y%m%d-%H%M%S")

[ "$new_run" = true ] && [ "$pure_run" = true ] && usage "Options n (new run) and p (pure run) are mutually exclusive."

if [ "$dry_run" = true ]; then log::info "Starting dry run"; fi
if [ "$new_run" = true ]; then log::info "Starting new run"; fi
if [ "$pure_run" = true ]; then log::info "Starting pure run"; fi
if [ -z "$cores" ]; then cores="all"; log::info "cores not provided, using all cores"; fi

if [ ! "$dry_run" = true ]; then
        log::info "Pulling latest rpgolota/privpurge from docker"
        docker pull rpgolota/privpurge
        log::info "Deactivating conda"
        conda deactivate
        log::info "Activating local virtual environment"
        . .venv/bin/activate
        if [ ! -d "logs" ]; then
                log::info "Making logs folder"
                mkdir logs
        fi
        if [ "$new_run" = true ]; then
                log::info "Running snakemake clean rule"
                snakemake --cores 1 clean
        elif [ "$pure_run" = true ]; then
                log::info "Running snakemake clean_all rule"
                snakemake --cores 1 clean_all
        fi
        log::info "Running snakemake"
        snakemake --cores "$cores" --keep-going > logs/"$run_id".txt
else
        log::info "Pulling latest rpgolota/privpurge from docker"
        log::dry_run "docker pull rpgolota/privpurge"
        log::info "Deactivating conda"
        log::dry_run "conda deactivate"
        log::info "Activating local virtual environment"
        log::dry_run ". .venv/bin/activate"
        if [ ! -d "logs" ]; then
                log::info "Making logs folder"
                log::dry_run "mkdir logs"
        fi
        if [ "$new_run" = true ]; then
                log::info "Running snakemake clean rule"
                log::dry_run "snakemake --cores 1 clean"
        elif [ "$pure_run" = true ]; then
                log::info "Running snakemake clean_all rule"
                log::dry_run "snakemake --cores 1 clean_all"
        fi
        log::info "Running snakemake"
        log::dry_run "snakemake --cores "$cores" --keep-going > logs/"$run_id".txt"
fi

