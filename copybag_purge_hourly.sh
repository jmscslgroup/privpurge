# place inside folder containing run.sh
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR
bash run.sh sync --age=120 --pull=private
bash run.sh copybag --cores=all
bash run.sh purge --cores=all
bash run.sh sync --age=120 --push=publishable