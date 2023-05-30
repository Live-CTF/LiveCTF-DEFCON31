default: apply

install:
	sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
	wget -O- https://apt.releases.hashicorp.com/gpg | \
		gpg --dearmor | \
		sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
	gpg --no-default-keyring \
		--keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
		--fingerprint
	sudo apt update
	sudo apt-get install terraform

init:
	terraform init

plan:
	terraform plan

apply:
	terraform apply

destroy:
	python3 cleanup-hostkeys.py
	terraform destroy

.PHONY: default install init plan apply destroy inventory
