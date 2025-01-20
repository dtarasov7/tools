curl -X POST "http://<radosgw-endpoint>/admin/user" \
     --user "ansible-access-key:ansible-secret-key" \
     -H "Content-Type: application/json" \
     -d '{
           "uid": "new-user",
           "display_name": "New Ceph User",
           "email": "newuser@example.com",
           "generate_key": true,
           "key-type": "s3"
         }'
