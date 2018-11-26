#!/bin/bash

# Copy certs
cp ~/galahad-config/elasticsearch_keys/kirk-keystore.jks ~/docker-virtue/elastic/esearch/searchguard/config/kirk-keystore.jks
cp ~/galahad-config/elasticsearch_keys/truststore.jks ~/docker-virtue/elastic/esearch/searchguard/config/truststore.jks
cp ~/galahad-config/elasticsearch_keys/node-0-keystore.jks ~/docker-virtue/elastic/esearch/searchguard/config/node-0-keystore.jks

cp ~/galahad-config/elasticsearch_keys/ca/root-ca.pem ~/docker-virtue/elastic/kibana/config/root-ca.pem
cp ~/galahad-config/elasticsearch_keys/ca/signing-ca.pem ~/docker-virtue/elastic/kibana/config/signing-ca.pem
cp ~/galahad-config/elasticsearch_keys/kibana.crt.pem ~/docker-virtue/elastic/kibana/config/kibana.crt.pem
cp ~/galahad-config/elasticsearch_keys/kibana.key.pem ~/docker-virtue/elastic/kibana/config/kibana.key.pem

# Build and start docker stack
sudo docker-compose build
sudo docker-compose up &

# Run setup script
docker-compose exec -T elasticsearch bin/init_sg.sh