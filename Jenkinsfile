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
/*                 notifyEvents message: "#News_Backend 🛠 Building New Container...", token: '7yi9o1VBd3mz-JP2JhQOICo3Y5zgPHGk'*/
                sh "docker-compose build"
/*                 notifyEvents message: "#News_Backend ⛔️️ Stopping Previous Container...", token: '7yi9o1VBd3mz-JP2JhQOICo3Y5zgPHGk'*/
                echo "Recreating containers..."
/*                 notifyEvents message: "#News_Backend 🐳 Upping New Container...", token: '7yi9o1VBd3mz-JP2JhQOICo3Y5zgPHGk' */
                sh "docker-compose up -d"
                echo "Deployed!"
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