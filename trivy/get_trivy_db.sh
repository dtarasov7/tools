#!/bin/bash
./run_trivy_docker.sh --download-db-only --quiet
if [ -f "trivy_db.tgz" ]; then
    rm trivy_db.tgz
fi
tar czf trivy_db.tgz ./db
