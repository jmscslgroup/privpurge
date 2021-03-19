<h1 align="center">privpurge</h1>
<h4 align="center">Purging privacy regions from collected data.</h4>


<p align="center">
<a href="https://github.com/jmscslgroup/privpurge/actions/workflows/code_test.yml"><img alt="Code Test" src="https://github.com/jmscslgroup/privpurge/workflows/Code%20Test/badge.svg"></a>
<a href="https://github.com/jmscslgroup/privpurge/actions/workflows/black.yml"><img alt="Lint Check" src="https://github.com/jmscslgroup/privpurge/workflows/Lint/badge.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

---

## Installing

- `pip install git+https://github.com/jmscslgroup/privpurge`

## Running

- `privpurge <CANFILE> <GPSFILE> -z <ZONEFILE> -o <OUTPUT_DIR>`

## Format (regex)

- Can/Gps Files: `r"(\d{4}(?:-\d{2}){5})_(.{17})_(?:CAN|GPS)_Messages?.csv"`
- Zonefiles: `r"zonefile_(.{17}).json"`

## Running as a container

- Volumes are just recommendations, and do not need to be used in the way shown.
- Only default directory is /data, in which the working directory is located. Can be overwritten by -w flag.

##### Use the following command to run

```
docker run --rm \ 
    -v <ZONE_PATH>:/zone \
    -v <DATA_PATH>:/data \ 
    -v <OUT_PATH>:/build \
    rpgolota/privpurge <CANFILE> <GPSFILE> -z /zone/<ZONEFILE> -o /build
```
