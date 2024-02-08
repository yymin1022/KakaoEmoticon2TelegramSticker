pipeline {
    agent any

    environment {
        TELEGRAM_BOT_ID = credentials("telegram-botid-yymin1022")
        TELEGRAM_CHAT_ID = credentials("telegram-chatid-yymin1022")

        CURRENT_BUILD_NUMBER = "${currentBuild.number}"
        GIT_MESSAGE = sh(returnStdout: true, script: "git log -n 1 --format=%s ${GIT_COMMIT}").trim()
        GIT_AUTHOR = sh(returnStdout: true, script: "git log -n 1 --format=%ae ${GIT_COMMIT}").trim()
        GIT_COMMIT_SHORT = sh(returnStdout: true, script: "git rev-parse --short ${GIT_COMMIT}").trim()
        GIT_INFO = "Branch(Version): ${GIT_BRANCH}\nLast Message: ${GIT_MESSAGE}\nAuthor: ${GIT_AUTHOR}\nCommit: ${GIT_COMMIT_SHORT}"
        TEXT_BREAK = "New Build Task Started !!"
        TEXT_PRE_BUILD = "${TEXT_BREAK}\n${GIT_INFO}\n${JOB_NAME}\n\nBuild가 시작되었습니다."

        TEXT_SUCCESS_BUILD = "${JOB_NAME} Build가 성공하였습니다."
        TEXT_FAILURE_BUILD = "${JOB_NAME} Build가 실패하였습니다."
    }

    stages {
        stage("Setup Build Environment") {
            steps {
                script {
                    DOCKERHUB_CREDENTIAL = "dockerhub-yymin1022"
                    DOCKER_IMAGE_NAME = "kakao-emoticon-to-telegram-sticker"
                    DOCKER_IMAGE_STORAGE = "yymin1022"
                    DOCKER_IMAGE_TAG = "release1"

                    sh "curl --location --request POST 'https://api.telegram.org/bot${TELEGRAM_BOT_ID}/sendMessage' --form text='${TEXT_PRE_BUILD}' --form chat_id='${TELEGRAM_CHAT_ID}'"
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
    
    post {
        success {
            script{
                sh "curl --location --request POST 'https://api.telegram.org/bot${TELEGRAM_BOT_ID}/sendMessage' --form text='${TEXT_SUCCESS_BUILD}' --form chat_id='${TELEGRAM_CHAT_ID}'"
            }
        }
        failure {
            script{
                sh "curl --location --request POST 'https://api.telegram.org/bot${TELEGRAM_BOT_ID}/sendMessage' --form text='${TEXT_FAILURE_BUILD}' --form chat_id='${TELEGRAM_CHAT_ID}'"
            }
        }
    }
}
