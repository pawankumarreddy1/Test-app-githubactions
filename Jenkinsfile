pipeline {
    agent {
        docker {
            image 'google/cloud-sdk:slim'
        }
    }

    options {
        skipDefaultCheckout(true)
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/pawankumarreddy1/Test-app-githubactions.git'
                    ]]
                ])
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                echo "Building Docker image..."
                docker build -t test-app:latest .
                '''
            }
        }

        stage('Push Docker Image to GCR') {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    string(credentialsId: 'gcp-project-id', variable: 'PROJECT_ID'),
                    string(credentialsId: 'gcp-region', variable: 'REGION')
                ]) {

                    sh '''
                    echo "Authenticating Docker to GCR..."
                    gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
                    gcloud auth configure-docker gcr.io --quiet

                    echo "Tagging and pushing image..."
                    docker tag test-app:latest gcr.io/$PROJECT_ID/test-app:latest
                    docker push gcr.io/$PROJECT_ID/test-app:latest
                    '''
                }
            }
        }

        stage('Deploy to Cloud Run') {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    string(credentialsId: 'gcp-project-id', variable: 'PROJECT_ID'),
                    string(credentialsId: 'gcp-region', variable: 'REGION')
                ]) {

                    sh '''
                    echo "Deploying to Cloud Run..."

                    gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"

                    gcloud run deploy test-app \
                        --image gcr.io/$PROJECT_ID/test-app:latest \
                        --platform managed \
                        --region "$REGION" \
                        --allow-unauthenticated
                    '''
                }
            }
        }
    }
}


