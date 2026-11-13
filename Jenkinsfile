pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker compose -p lostandfound build web'
            }
        }

        stage('Deploy Stack') {
            steps {
                sh 'docker compose -p lostandfound up -d --no-deps --build web nginx'
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    sleep 3
                    curl -f http://lostfound_nginx:80/ > /dev/null
                    echo "findIt deployed and healthy!"
                '''
            }
        }
    }
}