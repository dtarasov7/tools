set -x
./run_trivy_docker.sh i --no-progress --ignore-unfixed -s HIGH,CRITICAL "$@"