config = {
    "zone_dir": "../../private-circles/zonefiles",
    "intermediate_dir": "snakemake-output",
    "build_dir": "../../publishable-circles",
    "input_dir": "../../private-circles"
} # find snakemake-output/ -type f | grep .err | sed 's/^.\{17\}//' | xargs -n 1 sh -c 'cp snakemake-output/$1 ../../publishable-circles/$1' sh

ZONEFILE_DIR = config['zone_dir']
BUILD_DIR = config['build_dir']
INTERMEDIATE_DIR = config['intermediate_dir']
INPUT_DIR = config['input_dir']

CAN_WILD = glob_wildcards(INPUT_DIR + "/{vin}/libpanda/{day_folder}/{day,.{10}}-{time}_{vin2}_CAN_Messages.csv") # CAN_Message not supported
ZONE_WILD = glob_wildcards(ZONEFILE_DIR+"/zonefile_{vin}.json")

def remove_not_in_vin(wildcard, check_vin):
    i = 0
    while i < len(wildcard.vin):
        if wildcard.vin[i] not in check_vin:
            for field in wildcard._fields:
                del getattr(wildcard, field)[i]
            i -= 1
        i += 1

remove_not_in_vin(CAN_WILD, ZONE_WILD.vin)

OUTPUT_FILES = expand(INTERMEDIATE_DIR + "/{vin}/libpanda/{day_folder}/{day}-{time}_{vin}.out", zip, day_folder=CAN_WILD.day_folder, day=CAN_WILD.day, time=CAN_WILD.time, vin=CAN_WILD.vin)

rule all:
    input:
        OUTPUT_FILES

rule create:
    input:
        canfile_find=INPUT_DIR + "/{vin}/libpanda/{day_folder}/{day}-{time}_{vin}_CAN_Messages.csv",
        gpsfile_find=INPUT_DIR + "/{vin}/libpanda/{day_folder}/{day}-{time}_{vin}_GPS_Messages.csv",
        zonefile_find=ZONEFILE_DIR + "/zonefile_{vin}.json"
    params:
        canfile="/input/{vin}/libpanda/{day_folder}/{day}-{time}_{vin}_CAN_Messages.csv",
        gpsfile="/input/{vin}/libpanda/{day_folder}/{day}-{time}_{vin}_GPS_Messages.csv",
        zonefile="/zonefiles/zonefile_{vin}.json",
        errfile=INTERMEDIATE_DIR + "/{vin}/libpanda/{day_folder}/{day}-{time}_{vin}.err",
        build_dir=BUILD_DIR + "/{vin}/libpanda/{day_folder}/",
        zone_dir=ZONEFILE_DIR,
        input_dir=INPUT_DIR
    output:
        INTERMEDIATE_DIR + "/{vin}/libpanda/{day_folder}/{day,.{10}}-{time}_{vin}.out"
    shell:
        """
        res=$(mkdir -p {params.build_dir} &&        \
            docker run --rm                         \
            -u $(id -u):$(id -g)                    \
            -v $(pwd)/{params.zone_dir}:/zonefiles  \
            -v $(pwd)/{params.build_dir}:/build     \
            -v $(pwd)/{params.input_dir}:/input     \
            -v $(pwd):/data                         \
            rpgolota/privpurge                      \
            {params.canfile}                        \
            {params.gpsfile}                        \
            -z /{params.zonefile}                   \
            -o /build 2>&1) && echo "$res" > {output} || echo "$res" > {params.errfile}
        """
        
rule clean:
    shell:
        """
        rm -rf {config[intermediate_dir]}
        """