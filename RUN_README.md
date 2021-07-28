# run.sh documentation

---

## Components
- sync
    - pushing and pulling from cyverse
- purge
    - running privpurge on private data, output in publishable
- stitch
    - running stich on private data, output in publishable
- copybag
    - copies bag file directories from private to publishable

---

## General arguments
`bash run.sh --help`

show help

`bash run.sh --dry <SUBCOMMAND>`

dry-run with subcommand, will only show what commands will run without running them

`bash run.sh <SUBCOMMAND>`

runs subcommand

---

## Subcommand arguments
### sync
`bash run.sh sync`

does nothing

`bash run.sh sync --pull=<LOCATION>`

pulls from cyverse to local location. Location options: [private, publishable, zones]

`bash run.sh sync --push=<LOCATION>`

pushes from local to cyverse location. Location options: [private, publishable, zones]

`bash run.sh sync --age=MINUTES ...`

works with either --pull or --push. Only syncs the files MINUTES old or newer.

### purge

`bash run.sh purge`

runs purge with default settings. cores set to all.

`bash run.sh purge --cores=CORES`
`bash run.sh purge -c CORES`

specify cores to use

`bash run.sh purge --clean`

runs snakemake rule clean to remove intermediate output directory

### stitch

`bash run.sh stitch`

runs stitch with default settings. cores set to all.

`bash run.sh stitch --cores=CORES`

`bash run.sh stitch -c CORES`

specify cores to use

`bash run.sh stitch --clean`

runs snakemake rule clean to remove intermediate output directory

### copybag

`bash run.sh copybag`

runs copybag with default settings. cores set to all.

`bash run.sh copybag --cores=CORES`

`bash run.sh copybag -c CORES`

specify cores to use

---

## Requirements to run
### general requirements
- logging.shlib
- config.shlib
- config.cfg

Note all paths are relative to run.sh location.
### sync
- icommands installed
- config.cfg entries format: location (description) [default location]
    - zones (location of zone folder locally) [../../private-circles/zonefiles]
    - private (location of private folder locally) [../../private-circles]
    - publishable (location of publishable folder locally) [../../publishable-circles]
    - izones (location of zone folder on cyverse) [private-circles/zonefiles on cyverse]
    - iprivate (location of private folder on cyverse) [private-circles on cyverse]
    - ipublishable (location of publishable folder on cyverse) [publishable-circles on cyverse]
### purge
- privpurge snakefile downloaded locally
- a virtual environment folder .venv installed with python3 and snakemake in privpurge directory
- config.cfg entries
    - privpurge_dir (location where privpurge is installed) [../privpurge]
### stitch
- stitch git cloned locally
- a virtual environment folder .venv installed with python3, snakemake, and requirements required by stitch in stitch directory
- config.cfg entries
    - stitch_dir (location where stitch is installed) [../stitch]
### copybag
- copybag snakefile downloaded locally
- a virtual environment folder .venv installed with python3 and snakemake in copybag directory
- config.cfg entries
    - copybag_dir (location where copybag is installed) [../copybag]