# You need to install sshpass to run the script correctly

bold=$(tput bold)
normal=$(tput sgr0)
echo "${bold}*** Script de Deployment ***${normal}"

export SSHPASS='qazedctgb00'

###

echo -e "\n${bold}* Cópia do código a executar no servidor *${normal}"

sshpass -e sftp -o StrictHostKeyChecking=no grupo1@192.168.85.208 << EOF
	put -r . ES/
	bye
EOF

###

echo -e "\n${bold}* Execução do código no servidor *${normal}"

sshpass -e ssh -t -t -o StrictHostKeyChecking=no grupo1@192.168.85.208 << EOF
	cd ES/
	. venv/bin/activate
	docker-compose up --build
	exit
EOF
