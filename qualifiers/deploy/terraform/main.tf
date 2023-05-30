terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.38.2"
    }
  }

  required_version = ">= 1.4.4"
}

locals {
  server_settings = {
    web = {
        "web1.livectf.local" = { ip = "10.0.1.11", type = "cpx51", labels = { bastion = 1, web = 1, database = 1, registry = 1, rabbitmq = 1, redis = 1 } },
    }
    builders = {
        #"builder01.livectf.local" = { ip = "10.0.1.21", type = "cpx51", labels = { builder = 1 } },
        #"builder02.livectf.local" = { ip = "10.0.1.22", type = "cpx51", labels = { builder = 1 } },
        #"builder03.livectf.local" = { ip = "10.0.1.23", type = "cpx51", labels = { builder = 1 } },
        #"builder04.livectf.local" = { ip = "10.0.1.24", type = "cpx51", labels = { builder = 1 } },
        #"builder05.livectf.local" = { ip = "10.0.1.25", type = "cpx51", labels = { builder = 1 } },
        #"builder06.livectf.local" = { ip = "10.0.1.26", type = "cpx51", labels = { builder = 1 } },
        #"builder07.livectf.local" = { ip = "10.0.1.27", type = "cpx51", labels = { builder = 1 } },
        #"builder08.livectf.local" = { ip = "10.0.1.28", type = "cpx51", labels = { builder = 1 } },
        #"builder09.livectf.local" = { ip = "10.0.1.29", type = "cpx51", labels = { builder = 1 } },
        #"builder10.livectf.local" = { ip = "10.0.1.30", type = "cpx51", labels = { builder = 1 } },
        #"builder11.livectf.local" = { ip = "10.0.1.31", type = "cpx51", labels = { builder = 1 } },
        #"builder12.livectf.local" = { ip = "10.0.1.32", type = "cpx51", labels = { builder = 1 } },
        #"builder13.livectf.local" = { ip = "10.0.1.33", type = "cpx51", labels = { builder = 1 } },
        #"builder14.livectf.local" = { ip = "10.0.1.34", type = "cpx51", labels = { builder = 1 } },
        #"builder15.livectf.local" = { ip = "10.0.1.35", type = "cpx51", labels = { builder = 1 } },
        #"builder16.livectf.local" = { ip = "10.0.1.36", type = "cpx51", labels = { builder = 1 } },
        #"builder17.livectf.local" = { ip = "10.0.1.37", type = "cpx51", labels = { builder = 1 } },
        #"builder18.livectf.local" = { ip = "10.0.1.38", type = "cpx51", labels = { builder = 1 } },
        #"builder19.livectf.local" = { ip = "10.0.1.39", type = "cpx51", labels = { builder = 1 } },
        #"builder20.livectf.local" = { ip = "10.0.1.40", type = "cpx51", labels = { builder = 1 } },

    }
    runners = {
        #"runner01.livectf.local" = { ip = "10.0.1.61", type = "cpx51", labels = { runner = 1 } },
        #"runner02.livectf.local" = { ip = "10.0.1.62", type = "cpx51", labels = { runner = 1 } },
        #"runner03.livectf.local" = { ip = "10.0.1.63", type = "cpx51", labels = { runner = 1 } },
        #"runner04.livectf.local" = { ip = "10.0.1.64", type = "cpx51", labels = { runner = 1 } },
        #"runner05.livectf.local" = { ip = "10.0.1.65", type = "cpx51", labels = { runner = 1 } },
        #"runner06.livectf.local" = { ip = "10.0.1.66", type = "cpx51", labels = { runner = 1 } },
        #"runner07.livectf.local" = { ip = "10.0.1.67", type = "cpx51", labels = { runner = 1 } },
        #"runner08.livectf.local" = { ip = "10.0.1.68", type = "cpx51", labels = { runner = 1 } },
        #"runner09.livectf.local" = { ip = "10.0.1.69", type = "cpx51", labels = { runner = 1 } },
        #"runner10.livectf.local" = { ip = "10.0.1.70", type = "cpx51", labels = { runner = 1 } },
    }
    monitor = {
        #"monitor.livectf.local" = { ip = "10.0.1.81", type = "cpx51", labels = { monitor = 1 } },
    }
  }

  sshkeys = ["negasora2", "negasora1", "psifertex3", "psifertex2", "psifertex1", "CouleeApps1", "CouleeApps2", "ZetaTwo2018"]
}

variable "hcloud_token" {
  sensitive = true # Requires terraform >= 0.14
}

provider "hcloud" {
  token = var.hcloud_token
}

resource "hcloud_floating_ip_assignment" "web-ip-assignment" {
  floating_ip_id = "[REDACTED]" # TODO (P0): Add new static ip
  server_id      = hcloud_server.livectf-web["web1.livectf.local"].id
}

resource "hcloud_network" "network" {
  name     = "hashr_network"
  ip_range = "10.0.0.0/16"
}

resource "hcloud_network_subnet" "network-subnet" {
  type         = "cloud"
  network_id   = hcloud_network.network.id
  network_zone = "eu-central"
  ip_range     = "10.0.1.0/24"
}

resource "hcloud_server" "livectf-builder" {
  for_each      = local.server_settings.builders

  name        = each.key
  server_type = each.value.type
  image       = "ubuntu-22.04"
  location    = "hel1"
  ssh_keys    = local.sshkeys
  labels      = each.value.labels

  network {
    network_id = hcloud_network.network.id
    ip         = each.value.ip
  }

  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }

  depends_on = [
    hcloud_network_subnet.network-subnet
  ]
}

resource "hcloud_volume" "livectf-builder" {
  for_each      = local.server_settings.builders

  name      = format("storage.%s", each.key)
  size      = 50
  server_id = hcloud_server.livectf-builder[each.key].id
  automount = false
  format    = "xfs"
  labels    = {role: "docker"}
}

resource "hcloud_server" "livectf-runner" {
  for_each      = local.server_settings.runners

  name        = each.key
  server_type = each.value.type
  image       = "ubuntu-22.04"
  location    = "hel1"
  ssh_keys    = local.sshkeys
  labels      = each.value.labels

  network {
    network_id = hcloud_network.network.id
    ip         = each.value.ip
  }

  public_net {
    ipv4_enabled = false
    ipv6_enabled = true
  }

  depends_on = [
    hcloud_network_subnet.network-subnet
  ]
}

resource "hcloud_volume" "livectf-runner" {
  for_each      = local.server_settings.runners

  name      = format("storage.%s", each.key)
  size      = 50
  server_id = hcloud_server.livectf-runner[each.key].id
  automount = false
  format    = "xfs"
  labels    = {role: "docker"}
}

resource "hcloud_server" "livectf-web" {
  for_each      = local.server_settings.web

  name        = each.key
  server_type = each.value.type
  image       = "ubuntu-22.04"
  location    = "hel1"
  ssh_keys    = local.sshkeys
  labels      = each.value.labels

  network {
    network_id = hcloud_network.network.id
    ip         = each.value.ip
  }

  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }

  depends_on = [
    hcloud_network_subnet.network-subnet
  ]
}

resource "hcloud_server" "livectf-monitor" {
  for_each      = local.server_settings.monitor

  name        = each.key
  server_type = each.value.type
  image       = "ubuntu-22.04"
  location    = "hel1"
  ssh_keys    = local.sshkeys
  labels      = each.value.labels

  network {
    network_id = hcloud_network.network.id
    ip         = each.value.ip
  }

  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }

  depends_on = [
    hcloud_network_subnet.network-subnet
  ]
}

# generate inventory file for Ansible
resource "local_file" "hosts_ansible_inventory" {
  content = templatefile("${path.module}/hosts.tpl",
    {
      livectf-web = hcloud_server.livectf-web
      livectf-builder = hcloud_server.livectf-builder
      livectf-builder-volumes = hcloud_volume.livectf-builder
      livectf-runner = hcloud_server.livectf-runner
      livectf-runner-volumes = hcloud_volume.livectf-runner
      livectf-monitor = hcloud_server.livectf-monitor
      livectf-all = merge(hcloud_server.livectf-web, hcloud_server.livectf-builder, hcloud_server.livectf-runner, hcloud_server.livectf-monitor)
      
      server_settings = merge(local.server_settings.web, local.server_settings.builders, local.server_settings.runners, local.server_settings.monitor)
      subnet = hcloud_network_subnet.network-subnet
    }
  )
  filename = "hosts.yml"
  file_permission = "0644"
}

# generate SSH config file
resource "local_file" "hosts_ssh_config" {
  content = templatefile("${path.module}/hosts.ssh.tpl",
    {
      livectf-web = hcloud_server.livectf-web
      livectf-builder = hcloud_server.livectf-builder
      livectf-builder-volumes = hcloud_volume.livectf-builder
      livectf-runner = hcloud_server.livectf-runner
      livectf-runner-volumes = hcloud_volume.livectf-runner
      livectf-monitor = hcloud_server.livectf-monitor
      livectf-all = merge(hcloud_server.livectf-web, hcloud_server.livectf-builder, hcloud_server.livectf-runner, hcloud_server.livectf-monitor)
      
      server_settings = merge(local.server_settings.web, local.server_settings.builders, local.server_settings.runners, local.server_settings.monitor)
      subnet = hcloud_network_subnet.network-subnet
    }
  )
  filename = "hosts.ssh.conf"
  file_permission = "0644"
}
