#!/bin/bash
sudo usermod -aG docker your-user
docker pull docker.elastic.co/elasticsearch/elasticsearch:5.6.3
docker pull docker.elastic.co/kibana/kibana:5.6.3

chmod +x ~/docker-virtue/elastic/esearch/searchguard/bin/init_sg.sh