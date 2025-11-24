pipeline {
    agent any

    options {
        skipDefaultCheckout(true)   // avoid double checkout
    }

    environment {
        PROJECT_ID = credentials('gcp-project-id')
        GOOGLE_APPLICATION_CREDENTIALS = credentials('gcp-sa-key')
        REGION = credentials('gcp-region')
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: 'https://github.com/pawankumarreddy1/Test-app-githubactions.git']]
                ])
            }
        }

        stage('Setup GCloud') {
            steps {
                sh '''
                echo "Authenticating..."
                gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"

                gcloud config set project "$PROJECT_ID"
                gcloud config set run/region "$REGION"
                '''
            }
        }

        stage('Build & Deploy') {
            steps {
                sh '''
                echo "Deploying to Cloud Run..."
                gcloud run deploy test-app \
                    --image gcr.io/$PROJECT_ID/test-app:latest \
                    --platform managed \
                    --allow-unauthenticated \
                    --region "$REGION"
                '''
            }
        }
    }
}



