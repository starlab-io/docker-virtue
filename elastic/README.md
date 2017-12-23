# Syslog-ng setup

## Intall syslog-ng

To install using apt, first add 
	
	deb http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/xUbuntu_16.04 ./

To your sources.list to access the latest module.  This setup has been tested on version 3.11 and version 3.13.  

This will be tested on CentOS soon.  Instructions coming.  

## Install Elasticsearch

This setup is currently tested on elasticsearch version 5.6.3 for both the elastic nodes and for the modules used by syslog-ng.  To install elasticsearch for syslog-ng, just grab the following and tar -xvf it:

	curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.6.3.tar.gz

## Configuring Syslog-ng

Here is a sample configuration to connect to syslog-ng:

	@version: 3.12
	@module mod-java
	@include "scl.conf"


	source s_local { systemd-journal(); internal(); };

	destination d_file { file("/var/log/syslog-ng-msg"); };

	destination d_elastic {
		elasticsearch2(
			client-lib-dir("/path/to/elasticsearch/jars/")
			index("syslog-${YEAR}.${MONTH}.${DAY}")
			type("syslog")
			time-zone("UTC")
			client-mode("https")
			cluster("cluster-name")
			cluster-url("https://x.x.x.x:9200")
			java_keystore_filepath("/etc/syslog-ng/keystore.jks")
			java_keystore_password("changeit")
			java_truststore_filepath("/etc/syslog-ng/truststore.jks")
			java_truststore_password("changeit")
			http_auth_type("clientcert")
			resource("/etc/syslog-ng/elasticsearch.yml")
		);
	};

	log { source(s_local); destination(d_file); };
	log { source(s_local); destination(d_elastic); };

Where the elasticsearch.yml contains:

	cluster:
	  name: docker-cluster
	network:
	  host: x.x.x.x
	path:
	  home: /etc/syslog-ng
	  conf: /etc/syslog-ng
	searchguard.ssl.transport.enforce_hostname_verification: false


Documentation can be found:
* https://www.balabit.com/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html/configuring-destinations-elasticsearch2.html

See included files for specific configs used.

## Running syslog-ng

Syslog-ng can be run from systemctl, or you can run it manually with 
	
	syslog-ng -Fdv

# Elasticsearch/Kibana

Using docker/docker-compose should get everything up and running.  IP addresses will need to be adjusted, but otherwise this should work as is.   

## Elasticsearch setup

See the docker-compose/Dockerfile for setup commands.  If you want to install it locally, install elasticsearch 5.6.3 and be sure to run the searchguard plugn install shown in the elastic dockerfile.

See elastic/config/elasticsearch.yml for an example config.  This will work with the included files/certs, but IP's will need to be changed.  

A collection of scripts for generating a collection of certs for Elastic, Kibana, and the syslog-ng instances can be found:
* https://github.com/floragunncom/search-guard-ssl

Documentation can be found:
* http://docs.search-guard.com/latest/configuring-tls

## Starting Elasticsearch 

If you're starting the elasticsearch for the first time, after it has gotten going run 

	docker-compose exec -T elasticsearch bin/init_sg.sh

To set up the searchguard user roles and other settings.  

## Kibana setup

Also run from docker, see the included docker-compose/dockerfiles.  If you want to run locally, be sure to use version 5.6.3 and to install the searchguard plugin, as shown in kibana/Dockerfile.

## Seachguard users

The default users for the elasticsearch/kibana setup are:

* admin (password: admin): No restrictions for this user, can do everything
* kibanaro (password: kibanaro): Kibana user which can read every index
* kibanaserver (password: kibanaserver): User for the Kibana server (all permissions for .kibana index)

# Putting it all together

If everything is set up correctly, after running syslog-ng on one of our xen vms, you should begin to see logging data in your elastic instance.  

The above configruation puts output from syslog-ng to indexs of "syslog-YYYY.MM.DD".  Requesting

	https://ELASTIC_URL/syslog-*

Will show all indexes matching the wildcard, so all of our syslog-ng indexes.  Requesting

	https://ELASTIC_URL/syslog-YYYY.MM.DD/_search?pretty=1

will give a pretty printed discription of the contents of that given index.  

To view everything in Kibana, log into the Kibana instance as the admin user (or kibanaro if you already have everything set up and are just actually viewing logging data).  