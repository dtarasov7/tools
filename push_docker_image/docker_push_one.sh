set -x
ansible-playbook push_docker.yml -t d_one -l $1 $2 $3 $4 $5