config = {
    "zone_dir": "../zonefiles",
    "build_dir": "../build",
    "output_dir": "../output"
}

ZONEFILE_DIR=config['zone_dir']
BUILD_DIR=config['build_dir']
OUTPUT_DIR = config['output_dir']

CAN_WILD=glob_wildcards("{day}/{day2,.{10}}-{time}_{vin}_CAN_Messages.csv")
CAN_WILD_OLD=glob_wildcards("{day}/{day2,.{10}}-{time}_{vin}_CAN_Message.csv")
ZONE_WILD=glob_wildcards(ZONEFILE_DIR+"/zonefile_{vin}.json")

def remove_not_in_vin(wildcard, check_vin, fields=None):
    if fields is None:
        fields = wildcard._fields
    i = 0
    while i < len(wildcard.vin):
        if wildcard.vin[i] not in check_vin:
            for field in wildcard._fields:
                del getattr(wildcard, field)[i]
            i -= 1
        i += 1

remove_not_in_vin(CAN_WILD, ZONE_WILD.vin)
remove_not_in_vin(CAN_WILD_OLD, ZONE_WILD.vin)

OUTPUT_FILES = expand(OUTPUT_DIR+"/{day}/{day}-{time}_{vin}.out", zip, day=CAN_WILD.day, time=CAN_WILD.time, vin=CAN_WILD.vin)
OUTPUT_FILES_OLD = expand(OUTPUT_DIR+"/{day}/{day}-{time}_{vin}.out", zip, day=CAN_WILD_OLD.day, time=CAN_WILD_OLD.time, vin=CAN_WILD_OLD.vin)

rule all:
    input:
        OUTPUT_FILES, OUTPUT_FILES_OLD

CREATE_SCRIPT = """
                TMP=$(mktemp)
                evar=0
                res=$(docker run --rm                       \
                    -v $(pwd)/{params.zone_dir}:/zonefiles  \
                    -v $(pwd)/{params.build_dir}:/build     \
                    -v $(pwd):/data                         \
                    rpgolota/privpurge                      \
                    {input.canfile}                         \
                    {input.gpsfile}                         \
                    -z /{input.zonefile}                    \
                    -o /build 2> "$TMP") || evar=$? && true;
                err=$(cat "$TMP")
                if [ $evar -eq 0 ]
                then
                    echo $res > {output}
                else
                    echo $err > {params.errfile}
                fi
                """

rule create:
    input:
        canfile="{day}/{day}-{time}_{vin}_CAN_Messages.csv",
        gpsfile="{day}/{day}-{time}_{vin}_GPS_Messages.csv",
        zonefile=ZONEFILE_DIR+"/zonefile_{vin}.json"
    params:
        errfile=OUTPUT_DIR+"/{day}/{day}-{time}_{vin}.err",
        build_dir=BUILD_DIR+"/{day}",
        zone_dir=ZONEFILE_DIR
    output:
        OUTPUT_DIR+"/{day,.{10}}/{day}-{time}_{vin}.out"
    shell:
        CREATE_SCRIPT

rule create_old:
    input:
        canfile="{day}/{day}-{time}_{vin}_CAN_Message.csv",
        gpsfile="{day}/{day}-{time}_{vin}_GPS_Message.csv",
        zonefile=ZONEFILE_DIR+"/zonefile_{vin}.json"
    params:
        errfile=OUTPUT_DIR+"/{day}/{day}-{time}_{vin}.err",
        build_dir=BUILD_DIR+"/{day}",
        zone_dir=ZONEFILE_DIR
    output:
        OUTPUT_DIR+"/{day,.{10}}/{day}-{time}_{vin}.out"
    shell:
        CREATE_SCRIPT
        
rule clean:
    shell: f"rm -rf {OUTPUT_DIR}"

rule clean_all:
    shell: f"rm -rf {OUTPUT_DIR} && rm -rf {BUILD_DIR}"