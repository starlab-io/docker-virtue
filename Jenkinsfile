pipeline {
    agent any

    stages {

	stage('Build') {

	    environment {
		LICENSE_SIG_B64 = credentials('6efb8436-9531-4f3c-9123-d532a983257d')
		LICENSE_TXT_B64 = credentials('2772d28e-95b4-4289-89c6-87f3a8b221fb')
	    }
	    steps {
		git credentialsId: 'f59ff73f-97a3-4095-8804-a7c88134d824', url: 'git@github.com:starlab-io/docker-virtue.git'

		sh '''#!/bin/bash

cd virtue

echo $LICENSE_SIG_B64 | base64 -d > app-containers/cxlicense.sig
echo $LICENSE_TXT_B64 | base64 -d > app-containers/cxlicense.txt

echo "--------------- Set up venv ---------------"
python3 -m venv virtue-venv
. virtue-venv/bin/activate
pip3 install -r requirements.txt

echo "--------------- IMAGES ---------------"
python3 build.py --list
echo "--------------------------------------"

python3 build.py 

echo "--------------- Cleaning Up ---------------"
deactivate
rm -rf virtue-venv
rm app-containers/cxlicense.sig
rm app-containers/cxlicense.txt
                '''
	    }
	}
    }
}
