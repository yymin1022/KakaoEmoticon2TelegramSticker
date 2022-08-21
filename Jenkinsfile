pipeline {
    agent any

    stages {
        stage("Set Variable") {
            steps {
                script {
                    DOCKERHUB_CREDENTIAL = "dockerhub-yymin1022"
                    DOCKER_IMAGE_NAME = "kakao-emoticon-to-telegram-sticker"
                    DOCKER_IMAGE_STORAGE = "yymin1022"
                    DOCKER_IMAGE_TAG = "release1"
                }
            }
        }

        stage("Build Docker Image") {
            steps {
                script {
                    image = docker.build("${DOCKER_IMAGE_STORAGE}/${DOCKER_IMAGE_NAME}")
                }
            }
        }

        stage("Push Docker Image to Dockerhub") {
            steps {
                script {
                    docker.withRegistry("", DOCKERHUB_CREDENTIAL) {
                        image.push("$DOCKER_IMAGE_TAG")
                        image.push("latest")
                    }
                }
            }
        }
    }

}