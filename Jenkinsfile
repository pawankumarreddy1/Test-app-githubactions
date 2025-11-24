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

        stage('Setup GCloud') {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    string(credentialsId: 'gcp-project-id', variable: 'PROJECT_ID'),
                    string(credentialsId: 'gcp-region', variable: 'REGION')
                ]) {
                    sh '''
                    echo "Authenticating..."
                    gcloud --version

                    # Authenticate using the service account file
                    gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"

                    # Configure project and region
                    gcloud config set project "$PROJECT_ID"
                    gcloud config set run/region "$REGION"
                    '''
                }
            }
        }

        stage('Build & Deploy') {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    string(credentialsId: 'gcp-project-id', variable: 'PROJECT_ID'),
                    string(credentialsId: 'gcp-region', variable: 'REGION')
                ]) {
                    sh '''
                    echo "Deploying to Cloud Run..."

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

