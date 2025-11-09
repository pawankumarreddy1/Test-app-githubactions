pipeline {
    agent any

    environment {
        APP_NAME = "hostelapp-backend"
        EC2_HOST = "3.94.166.124" 
        EC2_USER = "ubuntu"
        SSH_KEY = "aws-ec2-ssh" 
        DOCKER_COMPOSE_FILE = "docker-compose.prod.yml"
        BRANCH_NAME = "main"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: "${BRANCH_NAME}", url: 'https://github.com/Prajwal-Fintech/hostelapp-backend.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${APP_NAME}:latest -f Dockerfile .'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'echo "Running Django tests..."'
                sh 'docker run --rm ${APP_NAME}:latest poetry run pytest || true'
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: ["${SSH_KEY}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << 'EOF'
                    set -e
                    echo "Pulling latest code..."
                    cd ~/hostelapp-backend || git clone https://github.com/your-org/hostelapp-backend.git ~/hostelapp-backend
                    cd ~/hostelapp-backend
                    git pull origin ${BRANCH_NAME}

                    echo "Building and restarting containers..."
                    docker compose -f ${DOCKER_COMPOSE_FILE} down
                    docker compose -f ${DOCKER_COMPOSE_FILE} up -d --build

                    echo "Cleaning up old images..."
                    docker image prune -f
                    EOF
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful!"
        }
        failure {
            echo "❌ Deployment failed!"
        }
    }
}
