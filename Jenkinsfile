pipeline {
    agent any

    environment {
        PATH = "$PATH:/usr/local/bin"
    }

    stages {
        stage("Deploy Prod") {
            when {
                branch "master"
            }
            steps {
                echo "Deploying and Building..."
                sendTelegram('Building new containers 🛠\n Commit message: ${sh "git log -1 --pretty=%B"}')
                sh "docker-compose build"
                echo "Recreating containers..."
                sendTelegram("Upping new containers 🐳")
                sh "docker-compose up -d"
                echo "Deployed!"
            }
        }
    }
     post {
         success {
             sendTelegram("🥃 Deploy Succeed 😍💕😋😎️")
         }
         failure {
             sendTelegram("Deploy Failed  😩😑😖😳")
         }
     }
}

void sendTelegram(message) {
    def encodedMessage = URLEncoder.encode(message, "UTF-8")

    withCredentials([string(credentialsId: 'telegramToken', variable: 'TOKEN'),
    string(credentialsId: 'telegramChatId', variable: 'CHAT_ID')]) {

        response = httpRequest (consoleLogResponseBody: true,
                contentType: 'APPLICATION_JSON',
                httpMode: 'GET',
                url: "https://api.telegram.org/bot$TOKEN/sendMessage?text=$encodedMessage&chat_id=$CHAT_ID&disable_web_page_preview=true",
                validResponseCodes: '200')
        return response
    }
}
