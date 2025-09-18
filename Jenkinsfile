pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "nimble-bonus-458610-m2"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "/usr/lib/google-cloud-sdk/bin"
    }

    stages {
        stage("Cloning from Github....."){
            steps {
                script {
                    echo 'Cloning the repository...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Sahilshaikh11/hybrid-anime-recommender']])
                    echo 'Repository cloned successfully.'
                }
            }
        }

        stage("Making a virtual Environment"){
            steps {
                script {
                    echo 'Making a virtual environment...'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc
                    '''
                }
            }
        }

        stage("DVC Pull"){
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script {
                        echo 'Pulling data from DVC remote storage...'
                        sh '''
                        . ${VENV_DIR}/bin/activate
                        dvc pull
                        '''
                        echo 'Data pulled successfully.'
                    }
                }
            }
        }

        stage("Build and Push Image to GCR"){
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script {
                        echo 'Building and Pushing Docker Image to GCR...'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet
                        docker build -t gcr.io/${GCP_PROJECT}/hybrid-anime-recommender:latest .
                        docker push gcr.io/${GCP_PROJECT}/hybrid-anime-recommender:latest
                        '''
                        echo 'Docker image built and pushed successfully.'
                    }
                }
            }
        }

        stage("Deploying to Kubernetes"){
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script {
                        echo 'Building and Pushing Docker Image to GCR...'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud container clusters get-credentials anime-recommender --region=us-central1
                        kubectl apply -f deployment.yaml
                        '''
                        echo 'Docker image built and pushed successfully.'
                    }
                }
            }
        }
    }
}