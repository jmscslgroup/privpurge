#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR"
source ./logging.shlib
source ./config.shlib

log::make_print_func "log::dry_run"  "${log_fore_magenta}"   "${log_set_bold}"

PURGE_LOC="$(config_get privpurge_dir)"
STITCH_LOC="$(config_get stitch_dir)"

LOGS_DIR="$SCRIPT_DIR/logs"

usage() {
if [ -n "$1" ]; then log::error "$1"; fi
cat >&2 << EOF
usage: bash ${0} [ -d | --dry] [-h | --help]
       bash ${0} sync [--pull=LOCATION] [--push=LOCATION] [--recent=TIME]
       bash ${0} purge [-c CORES | --cores=CORES] [--clean]
       bash ${0} stitch [-c CORES | --cores=CORES ] [--clean]

       main                       commands that work before specifying mode
       -h | --help                show help message and exit [optional].
       -d | --dry                 dry run, just show what commands would be run [optional].

       sync                       enter sync mode
       LOCATION                   {zones, private, publishable}
       --pull=LOCATION            sync LOCATION from cyverse to local [optional].
       --push=LOCATION            sync LOCATION to cyverse from local [optional].
       --age=TIME                 only sync files created after TIME, specified in minutes [optional].

       purge                      enter purge mode
       -c CORES | --cores=CORES   provide the number of cores to run with [optional].
       --clean                    run snakemake clean before snakemake [optional].

       stitch                     enter stitch mode
       -c CORES | --cores=CORES   provide the number of cores to run with [optional].
       --clean                    run snakemake clean before snakemake [optional].
EOF
exit 1
}

if [ $# -eq 0 ]; then usage; fi

while getopts :-:dh flag
do
        case "${flag}" in
                -)
                case "${OPTARG}" in
                        dry) dry_run=true;;
                        help) usage;;
                        *) [ "$OPTERR" = 1 ] && [ "${optspec:0:1}" != ":" ] && usage "Unknows option --${OPTARG}";;
                esac;;
                d) dry_run=true;;
                h) usage;;
                :) usage "missing argument for -$OPTARG";;
                \?) usage "unknown option: -$OPTARG";;
        esac
done
shift $((OPTIND-1))
OPTIND=1

[ "$dry_run" = true ] && log::info "Starting dry run."

run_type="$1"
shift
[[ "${run_type}" != @(sync|purge|stitch) ]] && usage "Invalid option for run type: ${run_type}"
log::info "Entering run type: ${run_type}"

if [ ! "$dry_run" = true ]; then

        if [ "${run_type}" = sync ]; then
                
                while getopts :-: flag
                do
                        case "${flag}" in
                                -)
                                case "${OPTARG}" in
                                        pull) usage "Must provide value for --pull";;
                                        pull=*) pull=${OPTARG#*=};;
                                        push) usage "Must provide value for --push";;
                                        push=*) push=${OPTARG#*=};;
                                        age) usage "Must provide value for --age";;
                                        age=*) age=${OPTARG#*=};;
                                        *) [ "$OPTERR" = 1 ] && [ "${optspec:0:1}" != ":" ] && usage "Unknows option --${OPTARG}";;
                                esac;;
                                :) usage "missing argument for -$OPTARG";;
                                \?) usage "unknown option: -$OPTARG";;
                        esac
                done
                shift $((OPTIND-1))
                OPTIND=1

                [[ ! -z "${pull}" && "${pull}" != @(zones|private|publishable) ]] && usage "Invalid option for pull: ${pull}"
                [[ ! -z "${push}" && "${push}" != @(zones|private|publishable) ]] && usage "Invalid option for push: ${push}"
                [ ! -z "$pull" ] && log::info "Got pull command: ${pull}"
                [ ! -z "$push" ] && log::info "Got push command: ${push}"
                if [ ! -z "$age" ]; then agecmd="--age=$age"; fi

                if [ ! -z "$pull" ]; then
                        dir="$(config_get $pull)"
                        idir="$(config_get i$pull)"
                        log::info "Syncing from cyverse (${idir}) to local (${dir})"
                        cmd="irsync -r -v ${agecmd} i:${idir} ${dir}"
                        $cmd
                fi

                if [ ! -z "$push" ]; then
                        dir="$(config_get $push)"
                        idir="$(config_get i$push)"
                        log::info "Syncing from local (${dir}) to cyverse (${idir})"
                        cmd="irsync -r -v ${agecmd} ${dir} i:${idir}"
                        $cmd
                fi

        elif [ "${run_type}" = purge ]; then

                if [ ! -d "$PURGE_LOC" ]; then
                        log::error "Could not find directory containing privpurge"
                        exit 1
                fi

                log::info "Entering privpurge directory..."
                cd "$PURGE_LOC"

                while getopts :c:-:h flag
                do
                        case "${flag}" in
                                -)
                                case "${OPTARG}" in
                                        cores) usage "Must provide value for --cores";; # val="${!OPTIND}"; OPTIND=$(( $OPTIND + 1 ));
                                        cores=*) cores=${OPTARG#*=};;
                                        clean) clean=true;;
                                        *) [ "$OPTERR" = 1 ] && [ "${optspec:0:1}" != ":" ] && usage "Unknows option --${OPTARG}";;
                                esac;;
                                c) cores=${OPTARG};;
                                :) usage "missing argument for -$OPTARG";;
                                \?) usage "unknown option: -$OPTARG";;
                        esac
                done
                shift $((OPTIND-1))
                OPTIND=1

                run_id=$(date +"%y%m%d-%H%M%S")
                run_id="purge_${run_id}"
                if [ "$clean" = true ]; then log::info "Starting clean run"; fi
                if [ -z "$cores" ]; then cores="all"; log::info "cores not provided, using all cores"; fi

                log::info "Pulling latest rpgolota/privpurge from docker"
                docker pull rpgolota/privpurge
                log::info "Activating local virtual environment"
                . .venv/bin/activate
                if [ ! -d "$LOGS_DIR" ]; then
                        log::info "Making logs folder"
                        mkdir $LOGS_DIR
                fi
                if [ "$clean" = true ]; then
                        log::info "Running snakemake clean rule"
                        snakemake --cores 1 clean
                fi
                log::info "Running snakemake"
                snakemake --cores "$cores" --keep-going &> $LOGS_DIR/"$run_id".txt

        elif [ "${run_type}" = stitch ]; then

                if [ ! -d "$STITCH_LOC" ]; then
                        log::error "Could not find directory containing privpurge"
                        exit 1
                fi

                log::info "Entering stitch directory..."
                cd "$STITCH_LOC"

                while getopts :c:-:h flag
                do
                        case "${flag}" in
                                -)
                                case "${OPTARG}" in
                                        cores) usage "Must provide value for --cores";; # val="${!OPTIND}"; OPTIND=$(( $OPTIND + 1 ));
                                        cores=*) cores=${OPTARG#*=};;
                                        clean) clean=true;;
                                        *) [ "$OPTERR" = 1 ] && [ "${optspec:0:1}" != ":" ] && usage "Unknows option --${OPTARG}";;
                                esac;;
                                c) cores=${OPTARG};;
                                :) usage "missing argument for -$OPTARG";;
                                \?) usage "unknown option: -$OPTARG";;
                        esac
                done
                shift $((OPTIND-1))
                OPTIND=1

                run_id=$(date +"%y%m%d-%H%M%S")
                run_id="stitch_${run_id}"
                if [ "$clean" = true ]; then log::info "Starting clean run"; fi
                if [ -z "$cores" ]; then cores="all"; log::info "cores not provided, using all cores"; fi

                log::info "Activating local virtual environment"
                . .venv/bin/activate
                if [ ! -d "$LOGS_DIR" ]; then
                        log::info "Making logs folder"
                        mkdir $LOGS_DIR
                fi
                if [ "$clean" = true ]; then
                        log::info "Running snakemake clean rule"
                        snakemake --cores 1 clean
                fi
                log::info "Running snakemake"
                snakemake --cores "$cores" --keep-going &> $LOGS_DIR/"$run_id".txt
        fi

else
        if [ "${run_type}" = sync ]; then
                while getopts :-: flag
                do
                        case "${flag}" in
                                -)
                                case "${OPTARG}" in
                                        pull) usage "Must provide value for --pull";;
                                        pull=*) pull=${OPTARG#*=};;
                                        push) usage "Must provide value for --push";;
                                        push=*) push=${OPTARG#*=};;
                                        age) usage "Must provide value for --age";;
                                        age=*) age=${OPTARG#*=};;
                                        *) [ "$OPTERR" = 1 ] && [ "${optspec:0:1}" != ":" ] && usage "Unknows option --${OPTARG}";;
                                esac;;
                                :) usage "missing argument for -$OPTARG";;
                                \?) usage "unknown option: -$OPTARG";;
                        esac
                done
                shift $((OPTIND-1))
                OPTIND=1

                [[ ! -z "${pull}" && "${pull}" != @(zones|private|publishable) ]] && usage "Invalid option for pull: ${pull}"
                [[ ! -z "${push}" && "${push}" != @(zones|private|publishable) ]] && usage "Invalid option for push: ${push}"
                [ ! -z "$pull" ] && log::info "Got pull command: ${pull}"
                [ ! -z "$push" ] && log::info "Got push command: ${push}"
                if [ ! -z "$age" ]; then agecmd="--age=$age"; fi

                if [ ! -z "$pull" ]; then
                        dir="$(config_get $pull)"
                        idir="$(config_get i$pull)"
                        log::info "Syncing from cyverse (${idir}) to local (${dir})"
                        cmd="irsync -r -v ${agecmd} i:${idir} ${dir}"
                        log::dry_run "$cmd"
                fi

                if [ ! -z "$push" ]; then
                        dir="$(config_get $push)"
                        idir="$(config_get i$push)"
                        log::info "Syncing from local (${dir}) to cyverse (${idir})"
                        cmd="irsync -r -v ${agecmd} ${dir} i:${idir}"
                        log::dry_run "$cmd"
                fi

        elif [ "${run_type}" = purge ]; then

                if [ ! -d "$PURGE_LOC" ]; then
                        log::error "Could not find directory containing privpurge"
                        exit 1
                fi

                log::info "Entering privpurge directory..."
                log::dry_run "cd $PURGE_LOC"

                while getopts :c:-:h flag
                do
                        case "${flag}" in
                                -)
                                case "${OPTARG}" in
                                        cores) usage "Must provide value for --cores";; # val="${!OPTIND}"; OPTIND=$(( $OPTIND + 1 ));
                                        cores=*) cores=${OPTARG#*=};;
                                        clean) clean=true;;
                                        *) [ "$OPTERR" = 1 ] && [ "${optspec:0:1}" != ":" ] && usage "Unknows option --${OPTARG}";;
                                esac;;
                                c) cores=${OPTARG};;
                                :) usage "missing argument for -$OPTARG";;
                                \?) usage "unknown option: -$OPTARG";;
                        esac
                done
                shift $((OPTIND-1))
                OPTIND=1

                run_id=$(date +"%y%m%d-%H%M%S")
                run_id="purge_${run_id}"
                if [ "$clean" = true ]; then log::info "Starting clean run"; fi
                if [ -z "$cores" ]; then cores="all"; log::info "cores not provided, using all cores"; fi

                log::info "Pulling latest rpgolota/privpurge from docker"
                log::dry_run "docker pull rpgolota/privpurge"
                log::info "Activating local virtual environment"
                log::dry_run ". .venv/bin/activate"
                if [ ! -d "$LOGS_DIR" ]; then
                        log::info "Making logs folder"
                        log::dry_run "mkdir $LOGS_DIR"
                fi
                if [ "$clean" = true ]; then
                        log::info "Running snakemake clean rule"
                        log::dry_run "snakemake --cores 1 clean"
                fi
                log::info "Running snakemake"
                log::dry_run "snakemake --cores "$cores" --keep-going &> $LOGS_DIR/"$run_id".txt"

        elif [ "${run_type}" = stitch ]; then

                if [ ! -d "$STITCH_LOC" ]; then
                        log::error "Could not find directory containing stitch"
                        exit 1
                fi

                log::info "Entering stitch directory..."
                log::dry_run "cd $STITCH_LOC"

                while getopts :c:-:h flag
                do
                        case "${flag}" in
                                -)
                                case "${OPTARG}" in
                                        cores) usage "Must provide value for --cores";; # val="${!OPTIND}"; OPTIND=$(( $OPTIND + 1 ));
                                        cores=*) cores=${OPTARG#*=};;
                                        clean) clean=true;;
                                        *) [ "$OPTERR" = 1 ] && [ "${optspec:0:1}" != ":" ] && usage "Unknows option --${OPTARG}";;
                                esac;;
                                c) cores=${OPTARG};;
                                :) usage "missing argument for -$OPTARG";;
                                \?) usage "unknown option: -$OPTARG";;
                        esac
                done
                shift $((OPTIND-1))
                OPTIND=1

                run_id=$(date +"%y%m%d-%H%M%S")
                run_id="stitch_${run_id}"
                if [ "$clean" = true ]; then log::info "Starting clean run"; fi
                if [ -z "$cores" ]; then cores="all"; log::info "cores not provided, using all cores"; fi

                log::info "Activating local virtual environment"
                log::dry_run ". .venv/bin/activate"
                if [ ! -d "$LOGS_DIR" ]; then
                        log::info "Making logs folder"
                        log::dry_run "mkdir $LOGS_DIR"
                fi
                if [ "$clean" = true ]; then
                        log::info "Running snakemake clean rule"
                        log::dry_run "snakemake --cores 1 clean"
                fi
                log::info "Running snakemake"
                log::dry_run "snakemake --cores "$cores" --keep-going &> $LOGS_DIR/"$run_id".txt"
        fi

fi