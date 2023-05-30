%{ for server in [for s in livectf-all: s if contains(keys(s.labels), "bastion")] ~}
Host ${server.name}
    User root
    Hostname ${server.ipv4_address}
%{ endfor ~}

%{ for server in [for s in livectf-all: s if !contains(keys(s.labels), "bastion")] ~}
Host ${server.name}
    User root
    ProxyJump root@${[for s in livectf-all: s if contains(keys(s.labels), "bastion")][0].ipv4_address }
    Hostname ${server_settings[server.name].ip}

%{ endfor ~}
