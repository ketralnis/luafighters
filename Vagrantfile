Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/precise64"

  config.vm.provider "virtualbox" do |v|
    v.cpus = 2
    v.memory = 2048
  end

  guest_ip = "dhcp"

  if guest_ip == "dhcp"
    config.vm.network "private_network", type: guest_ip
  else
    config.vm.network "private_network", ip: guest_ip
  end

  config.vm.hostname = "luafighters.vm"

  # http
  config.vm.network "forwarded_port", host: 5000, guest: 5000

  # project synced folder
  config.vm.synced_folder  ".", "/home/vagrant/luafighters"

  config.vm.provision "shell", path: "./bootstrap.sh"
end
