# https://github.com/elastic/elasticsearch-docker
FROM docker.elastic.co/elasticsearch/elasticsearch:5.6.3

COPY searchguard/config/ config/
COPY searchguard/bin/ bin/

RUN elasticsearch-plugin install --batch com.floragunn:search-guard-5:5.6.3-16 \
	&& chmod +x \
	plugins/search-guard-5/tools/hash.sh \
	plugins/search-guard-5/tools/sgadmin.sh