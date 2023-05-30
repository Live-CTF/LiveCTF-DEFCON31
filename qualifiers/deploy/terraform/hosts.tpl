all:
  vars:
    ansible_user: root
    ansible_ssh_extra_args: '-R 5001:localhost:5001'
  hosts:
  children:
    web:
      hosts:
%{ for server in livectf-web ~}
        ${server.name}:
          ansible_host: ${server_settings[server.name].ip}
          private_ip: ${server_settings[server.name].ip}
          %{if !contains(keys(server.labels), "bastion") }ansible_ssh_common_args: '-J root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }'%{ endif }
%{ endfor ~}
    builder:
      hosts:
%{ for server in livectf-builder ~}
        ${server.name}:
          ansible_host: ${server_settings[server.name].ip}
          private_ip: ${server_settings[server.name].ip}
          volume_id: ${livectf-builder-volumes[server.name].id}
          %{if !contains(keys(server.labels), "bastion") }ansible_ssh_common_args: '-J root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }'%{ endif }
%{ endfor ~}
    runner:
      hosts:
%{ for server in livectf-runner ~}
        ${server.name}:
          ansible_host: ${server_settings[server.name].ip}
          private_ip: ${server_settings[server.name].ip}
          volume_id: ${livectf-runner-volumes[server.name].id}
          %{if !contains(keys(server.labels), "bastion") }ansible_ssh_common_args: '-J root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }'%{ endif }
%{ endfor ~}
    database:
      vars:
        subnet: "${subnet.ip_range}"
      hosts:
%{ for server in [for s in livectf-all: s if contains(keys(s.labels), "database")] ~}
        ${server.name}:
          ansible_host: ${server_settings[server.name].ip}
          private_ip: ${server_settings[server.name].ip}
          %{if !contains(keys(server.labels), "bastion") }ansible_ssh_common_args: '-J root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }'%{ endif }
%{ endfor ~}
    registry:
      hosts:
%{ for server in [for s in livectf-all: s if contains(keys(s.labels), "registry")] ~}
        ${server.name}:
          ansible_host: ${server_settings[server.name].ip}
          private_ip: ${server_settings[server.name].ip}
          %{if !contains(keys(server.labels), "bastion") }ansible_ssh_common_args: '-J root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }'%{ endif }
%{ endfor ~}
    rabbitmq:
      hosts:
%{ for server in [for s in livectf-all: s if contains(keys(s.labels), "rabbitmq")] ~}
        ${server.name}:
          ansible_host: ${server_settings[server.name].ip}
          private_ip: ${server_settings[server.name].ip}
          %{if !contains(keys(server.labels), "bastion") }ansible_ssh_common_args: '-J root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }'%{ endif }
%{ endfor ~}
    redis:
      hosts:
%{ for server in [for s in livectf-all: s if contains(keys(s.labels), "redis")] ~}
        ${server.name}:
          ansible_host: ${server_settings[server.name].ip}
          private_ip: ${server_settings[server.name].ip}
          %{if !contains(keys(server.labels), "bastion") }ansible_ssh_common_args: '-J root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }'%{ endif }
%{ endfor ~}
    monitor:
      hosts:
%{ for server in [for s in livectf-all: s if contains(keys(s.labels), "monitor")] ~}
        ${server.name}:
          ansible_host: ${server_settings[server.name].ip}
          private_ip: ${server_settings[server.name].ip}
          %{if !contains(keys(server.labels), "bastion") }ansible_ssh_common_args: '-J root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }'%{ endif }
%{ endfor ~}
    bastion:
      hosts:
%{ for server in [for s in livectf-all: s if contains(keys(s.labels), "bastion")] ~}
        ${server.name}:
          ansible_host: ${server.ipv4_address}
          private_ip: ${server_settings[server.name].ip}
          %{if !contains(keys(server.labels), "bastion") }ansible_ssh_common_args: '-J root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }'%{ endif }
%{ endfor ~}
    internal:
      hosts:
%{ for server in [for s in livectf-all: s if !contains(keys(s.labels), "bastion")] ~}
        ${server.name}:
          ansible_host: ${server_settings[server.name].ip}
          private_ip: ${server_settings[server.name].ip}
          %{if !contains(keys(server.labels), "bastion") }ansible_ssh_common_args: '-J root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }'%{ endif }
%{ endfor ~}
