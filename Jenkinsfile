pipeline {
    agent any

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
    }
}