pipeline {
    agent any

    environment {
        PROJECT_ID = "your-gcp-project-id"
        REGION = "asia-south1"
        SERVICE = "frontend-cloudrun-service"
        REPO = "frontend-repo"
        IMAGE = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/frontend:${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Node') {
            steps {
                sh 'node --version || true'
                sh 'npm --version || true'
            }
        }

        stage('Install Dependencies & Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build -t $IMAGE ."
            }
        }

        stage('Authenticate & Push Image') {
            steps {
                withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GCP_KEY')]) {
                    sh '''
                        gcloud auth activate-service-account --key-file=$GCP_KEY
                        gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
                    '''
                }
                sh "docker push $IMAGE"
            }
        }

        stage('Deploy to Cloud Run') {
            steps {
                withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GCP_KEY')]) {
                    sh '''
                        gcloud auth activate-service-account --key-file=$GCP_KEY
                        gcloud config set project $PROJECT_ID
                        gcloud run deploy $SERVICE \
                          --image=$IMAGE \
                          --platform=managed \
                          --region=$REGION \
                          --allow-unauthenticated \
                          --port=8080
                    '''
                }
            }
        }
    }
}

