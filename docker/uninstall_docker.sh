sudo apt-get purge docker-ce docker-ce-cli containerd.io -y

sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd

sudo apt-get remove docker docker-engine docker.io containerd runc -y

sudo apt autoremove -y