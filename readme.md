# Nested Ansible

The goal is to create a VM in vagrant which itself hosts one or more VMs to test ansible processes.  There was a reason for this but it escapes me at the moment.  Eventually, what I'd like to see would be a minimal set of commands to get python and ansible installed and then an ansible command to get the rest of the local host set up to create a VM which then gets set up to run its own VMs.  Might try for a bit of recursion where there's a playbook that will create a VM with a certain percentage of the host's RAM which then gets configured to do the same.

## Set up the local environment to run vagrant/libvirt

This is being run on a Debian 10 machine and I felt like learning some libvirt.  In previous ansible attempts, I was using virtualbox.  Nothing wrong with that, just felt like learning something else.

As I'm still learning, some of this might not be necessary.  One of the goals that I just remembered is to play with the setup of the host machine to find out what is really required rather than something working because random package X was installed by random package Y.  The following installs qemu and some of its requirements, ebtables for some network reason, libvirt packages, and vagrant itself.

    sudo apt-get install -y qemu qemu-kvm libvirt-clients libvirt-daemon-system ebtables libxslt-dev libxml2-dev libvirt-dev zlib1g-dev ruby-dev vagrant

Get python 3 set up for virtual environments.

    sudo apt-get install python-pip python3-pip python3-venv

Make it so running `python` will choose python3 instead of python2.

    sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2

Point pip to a local pypi cache so constant rebuilds will not eat up monthly data allotment.  See https://pypi.org/project/devpi-server/.

    python -m pip config set "global.index-url" http://local-pypi-cache-server.local/root/pypi/+simple/
    python -m pip config set "install.trusted-host" local-pypi-cache-server.local

## Create a simple VM

The included Vagrantfile describes a simple Debian box.  The comments should, hopefully, explain what each line is for.  In short:

* uses Debian Buster 64bit
* will not update the downloaded box in order to save on internet usage
* does not set up a shared folder between host and guest
* uses a pile of RAM and CPU as this VM will host other VMs
* sets up a connection to the host so qemu-guest-agent will function
* names the host "blarg.test" with ip 192.168.33.10

Now, start the VM.  If you don't already have the debian/buster64 box downloaded for libvirt, this might take a moment.

    vagrant up

## Set up the local environment to run ansible.
Using python3's venv (what I use on Debian)

    python -m venv --copies venv
    . venv/bin/activate

Or using pyenv (what I use on OSX)

    pyenv virtualenv --copies 3.8.2 ansible-test-venv
    pyenv local ansible-test-venv

Regardless, The first upgrades pip and installs wheel.  An upgraded pip is usually a good thing and wheel prevents the "Failed building wheel for ..." error messages.  The second installs ansible and libvirt.  The libvirt library is so python can query the VMs.

    pip install -r requirements-first.txt --upgrade
    pip install -r requirements-second.txt --upgrade

## Verify the inventory.

The included inventory file points to the VM created by the Vagrantfile and tells ansible the user and private key to use.  If you've changed any of that, the inventory file needs to reflect those changes.

## Configure some ansible settings

The `ansible.cfg` file holds some settings for ansible's behavior.  The `interpreter_python` setting silences the warnings about automatically determining which python interpreter to use.  The `auto_silent` setting tells ansible to just be quiet about it.  While not secure, turning `host_key_checking` off just makes dealing with often recreated VMs easier.  This suppresses the ssh question of `ECDSA key fingerprint is...` when first connecting.  Another way around it would be to manually connect to each VM and answer the question outside of ansible.  The `profile_tasks` callback just adds a nice report for each task and at the end to show how long everything took.  The default sorting is descending but is overridden here to be in executed order.

## Simple test to make sure ansible can see the VM.

This runs an adhoc command on the VM.  The `-a` arg is for adding arguments to the selected `-m` module.  When no module is specified, the `command` module is used.  The following could have `-m command` added and there would be no difference in behavior.

    ansible -i inventory.yml -a "free -h" machines
    vm1 | CHANGED | rc=0 >>
                  total        used        free      shared  buff/cache   available
    Mem:          9.8Gi       155Mi       9.4Gi       8.0Mi       166Mi       9.4Gi
    Swap:            0B          0B          0B

If you get the error below, just wait a few seconds and try again.  I haven't looked into why this happens.

    vm1 | UNREACHABLE! => {
        "changed": false,
        "msg": "Failed to connect to the host via ssh: ssh: connect to host 192.168.33.10 port 22: Connection timed out",
        "unreachable": true
    }

Just for fun, run the same command against the localhost.  Note the comma after `localhost` and the change from `machines` to `all`.  The comma tells ansible to treat the string as a list as it tries various ways to interpret the given inventory.  Since the inventory is just a list of hosts, there isn't a `machines` group so it was changed to the default `all` group.  Also, `-m command` is added here to show the behavior is the same as without it.

    ansible -i localhost, -m command -a "free -h" all
    localhost | CHANGED | rc=0 >>
                  total        used        free      shared  buff/cache   available
    Mem:           31Gi       1.4Gi        29Gi       9.0Mi       667Mi        29Gi
    Swap:          31Gi          0B        31Gi
