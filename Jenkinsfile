pipeline {
    agent any

    environment {
        PROJECT_ID = credentials('gcp-project-id')
        REGION = credentials('gcp-region')
        SERVICE_NAME = "django-backend"
        IMAGE_NAME = "django-backend"
        REPO = "asia-south1-docker.pkg.dev/${PROJECT_ID}/cloud-run-repo/${IMAGE_NAME}"
        GOOGLE_APPLICATION_CREDENTIALS = credentials('gcp-sa-key')
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Setup GCloud') {
            steps {
                sh """
                echo '${GOOGLE_APPLICATION_CREDENTIALS}' > gcloud-key.json

                gcloud auth activate-service-account --key-file=gcloud-key.json

                gcloud config set project ${PROJECT_ID}
                gcloud config set compute/region ${REGION}
                gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
                """
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build -t ${REPO}:latest ."
            }
        }

        stage('Docker Push') {
            steps {
                sh "docker push ${REPO}:latest"
            }
        }

        stage('Deploy to Cloud Run') {
            steps {
                sh """
                gcloud run deploy ${SERVICE_NAME} \
                    --image=${REPO}:latest \
                    --region=${REGION} \
                    --platform=managed \
                    --allow-unauthenticated \
                    --port=8080
                """
            }
        }
    }

    post {
        failure {
            echo "❌ Deployment Failed!"
        }
        success {
            echo "✅ Deployment successful!"
        }
    }
}


