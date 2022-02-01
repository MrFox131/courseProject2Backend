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
                sendTelegram("Deploying and Building")
/*                 notifyEvents message: "#News_Backend 🛠 Building New Container...", token: '7yi9o1VBd3mz-JP2JhQOICo3Y5zgPHGk'*/
                sh "docker-compose build"
                sendTelegram("docker-compose build")
/*                 notifyEvents message: "#News_Backend ⛔️️ Stopping Previous Container...", token: '7yi9o1VBd3mz-JP2JhQOICo3Y5zgPHGk'*/
                echo "Recreating containers..."
                sendTelegram("Uping")
/*                 notifyEvents message: "#News_Backend 🐳 Upping New Container...", token: '7yi9o1VBd3mz-JP2JhQOICo3Y5zgPHGk' */
                sh "docker-compose up -d"
                echo "Deployed!"
                sendTelegram("Done!")
            }
        }
    }
/*     post {
//         success {
//             notifyEvents message: "#News_Backend 🥃 Deploy Succeed 😍💕😋😎️", token: '7yi9o1VBd3mz-JP2JhQOICo3Y5zgPHGk'
//         }
//         failure {
//             notifyEvents message: '#News_Backend Deploy Failed  😩😑😖😳', token: '7yi9o1VBd3mz-JP2JhQOICo3Y5zgPHGk'
//         }
//     }*/
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
