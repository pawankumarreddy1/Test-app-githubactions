pipeline {
    agent {
        docker {
            image 'google/cloud-sdk:slim'
        }
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Setup GCloud') {
            steps {
                sh '''
                echo "Authenticating..."
                gcloud --version
                gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
                gcloud config set project "$PROJECT_ID"
                gcloud config set run/region "$REGION"
                '''
            }
        }

        stage('Build & Deploy') {
            steps {
                sh '''
                echo "Deploying..."
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



