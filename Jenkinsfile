pipeline {
    agent any

    // Wymaga wtyczki NodeJS i narzędzia skonfigurowanego w
    // Manage Jenkins → Tools pod nazwą "node-20"
    tools {
        nodejs 'node-20'
    }

    environment {
        REGISTRY        = 'docker.io'                  // np. ghcr.io lub adres prywatnego rejestru
        IMAGE_NAME      = 'mojafirma/simple-task-api'  // nazwa repozytorium w rejestrze
        REGISTRY_CREDS  = 'docker-registry-creds'      // ID poświadczeń (Username with password) w Jenkinsie
    }

    options {
        timeout(time: 30, unit: 'MINUTES')             // przerwij zawieszony build
        buildDiscarder(logRotator(numToKeepStr: '10')) // przechowuj 10 ostatnich buildów
        disableConcurrentBuilds()                      // jeden build naraz
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    // Krótki hash commita do tagowania obrazu
                    env.GIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${env.GIT_SHORT}"
                }
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'npm install'
            }
        }

        stage('Test') {
            steps {
                sh 'npm test'
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }

        stage('Build Docker image') {
            steps {
                sh """
                    docker build \
                      -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
                      -t ${REGISTRY}/${IMAGE_NAME}:latest \
                      .
                """
            }
        }

        stage('Push Docker image') {
            // Publikuj tylko z gałęzi main (działa w pipeline typu Multibranch)
            when {
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.REGISTRY_CREDS,
                    usernameVariable: 'REGISTRY_USER',
                    passwordVariable: 'REGISTRY_PASS'
                )]) {
                    // Pojedyncze cudzysłowy: zmienne rozwija powłoka, a hasło nie trafia do logu
                    sh '''
                        echo "$REGISTRY_PASS" | docker login "$REGISTRY" -u "$REGISTRY_USER" --password-stdin
                        docker push "$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
                        docker push "$REGISTRY/$IMAGE_NAME:latest"
                    '''
                }
            }
        }
    }

    post {
        always {
            // Wyloguj z rejestru i usuń lokalne obrazy, żeby nie zapychały dysku agenta
            sh """
                docker logout ${REGISTRY} || true
                docker rmi ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest || true
            """
        }
        success {
            echo "Build ${IMAGE_TAG} zakończony sukcesem"
        }
        failure {
            echo 'Build zakończony niepowodzeniem – sprawdź logi etapu, który nie przeszedł'
        }
    }
}
