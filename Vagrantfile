# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # buster == Debian 10.  Latest at the time of Vagrantfile creation.
  config.vm.box = "debian/buster64"
  # Don't want vagrant constantly downloading box updates just for these throw-away tests.
  config.vm.box_check_update = false
  # Do not set up a shared folder between the hose and guest.
  config.vm.synced_folder '.', '/vagrant', disabled: true
  config.nfs.verify_installed = false
  # Do not generate a new ssh key.  Uses an insecure key.
  config.ssh.insert_key = false
  # Tells the guest to use an apt proxy - https://hub.docker.com/r/sameersbn/apt-cacher-ng
  config.vm.provider :libvirt do |lv|
    # Adding a lot of RAM as this VM will host other VMs.
    lv.cpus = 4
    lv.memory = 10240
    # Am told these are required to nest VMs.
    lv.nested = true
    lv.cpu_mode = "host-model"
    # Create a virtio channel for use by the qemu-guest agent (time sync, snapshotting, etc)
    lv.channel :type => 'unix', :target_name => 'org.qemu.guest_agent.0', :target_type => 'virtio'
  end

  config.vm.define "blarg" do |vm|
    vm.vm.hostname = "blarg.test"
    vm.vm.network "private_network", ip: "192.168.33.10"
  end
end
