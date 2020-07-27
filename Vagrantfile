# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "debian/buster64"
  config.vm.box_check_update = false
  config.vm.synced_folder '.', '/vagrant', disabled: true
  config.ssh.insert_key = false
  config.vm.provider :libvirt do |lv|
    lv.cpus = 4
    lv.memory = 10240
    lv.nested = true
    lv.cpu_mode = "host-model"
    # Create a virtio channel for use by the qemu-guest agent (time sync, snapshotting, etc)
    lv.channel :type => 'unix', :target_name => 'org.qemu.guest_agent.0', :target_type => 'virtio'
  end
  config.nfs.verify_installed = false

  config.vm.define "blarg" do |web|
    web.vm.hostname = "blarg.test"
    web.vm.network "private_network", ip: "192.168.33.10"
  end
end
