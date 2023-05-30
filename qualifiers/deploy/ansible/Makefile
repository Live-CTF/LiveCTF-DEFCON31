deploy:
	ansible-playbook -i ../terraform/hosts.yml livectf-playbook.yml -e ctf_started=true

upgrade:
	ansible-playbook -i ../terraform/hosts.yml livectf-playbook.yml -e upgrade_runner=true -e upgrade_builder=true -e upgrade_web=true -e upgrade_api=true -e ctf_started=true

upgrade-web:
	ansible-playbook -i ../terraform/hosts.yml livectf-playbook.yml -e upgrade_web=true -e upgrade_api=true -e ctf_started=true

fix-playbook:
	ansible-playbook -i ../terraform/hosts.yml fix-playbook.yml --limit web -e upgrade_runner=true -e upgrade_builder=true -e upgrade_web=true -e upgrade_api=true -e ctf_started=true

upgrade-runner:
	ansible-playbook -i ../terraform/hosts.yml livectf-playbook.yml --limit runner -e upgrade_runner=true -e ctf_started=true

upgrade-builder:
	ansible-playbook -i ../terraform/hosts.yml livectf-playbook.yml --limit builder -e upgrade_builder=true -e ctf_started=true

dev:
	ansible-playbook -i ../terraform/hosts.yml dev-playbook.yml -e upgrade_runner=true -e upgrade_builder=true -e upgrade_web=true -e upgrade_api=true

prepare:
	docker run --rm -d -p 127.0.0.1:5001:5000 -p 172.17.0.1:5001:5000 --name registry registry:2

cleanup:
	docker stop registry

inventory:
	ansible-inventory -i ../terraform/hosts.yml --list

.PHONY: deploy prepare cleanup inventory
