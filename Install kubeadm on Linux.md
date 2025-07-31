Install kubeadm on Linux
https://v1-29.docs.kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/

sudo swapoff -a

PRE REQUISTE

cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# sysctl params required by setup, params persist across reboots
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

# Apply sysctl params without reboot
sudo sysctl --system

1. containerd
https://v1-29.docs.kubernetes.io/docs/setup/production-environment/container-runtimes/
https://github.com/containerd/containerd/blob/main/docs/getting-started.md
https://github.com/containerd/containerd/releases?page=2

wget https://github.com/containerd/containerd/releases/download/v1.7.22/containerd-1.7.22-linux-amd64.tar.gz
sudo tar Cxzvf /usr/local containerd-1.7.22-linux-amd64.tar.gz
sudo ln -s /usr/local/bin/containerd /usr/bin/containerd
https://raw.githubusercontent.com/containerd/containerd/main/containerd.service (service file link)

### create systemd file for containerd 
sudo vi /usr/lib/systemd/system/containerd.service

# Copyright The containerd Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target dbus.service

[Service]
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5

# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNPROC=infinity
LimitCORE=infinity

# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this version.
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target
#########################

sudo systemctl daemon-reload
sudo systemctl enable --now containerd

The default configuration can be generated via below command
sudo mkdir -p /etc/containerd/
sudo su
containerd config default > /etc/containerd/config.toml

vi /etc/containerd/config.toml
find SystemdCgroup & change it to true
SystemdCgroup = true
find pause:3.8 and replace with 3.9
registry.k8s.io/pause:3.9

sudo systemctl restart containerd


2. crictl 
https://github.com/kubernetes-sigs/cri-tools/blob/master/docs/crictl.md
https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.29.0/crictl-v1.29.0-linux-amd64.tar.gz
VERSION="v1.29.0" # check latest version in /releases page
wget https://github.com/kubernetes-sigs/cri-tools/releases/download/$VERSION/crictl-$VERSION-linux-amd64.tar.gz
sudo tar zxvf crictl-$VERSION-linux-amd64.tar.gz -C /usr/local/bin

cat <<EOF | sudo tee /etc/crictl.yaml
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
EOF


3. runc
https://github.com/opencontainers/runc/releases
wget https://github.com/opencontainers/runc/releases/download/v1.2.5/runc.amd64
install -m 755 runc.amd64 /usr/local/sbin/runc

4. cni
https://github.com/containernetworking/plugins/releases
wget https://github.com/containernetworking/plugins/releases/download/v1.3.0/cni-plugins-linux-amd64-v1.3.0.tgz
mkdir -p /opt/cni/bin
tar Cxzvf /opt/cni/bin cni-plugins-linux-amd64-v1.3.0.tgz


INSTALL KUBEADM
https://v1-29.docs.kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#installing-kubeadm-kubelet-and-kubectl

1. sudo setenforce 0
2. sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
3. cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.29/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.29/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF
4.Install kubelet, kubeadm and kubectl:
    sudo yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
5.sudo systemctl enable --now kubelet

Create Cluster Using Kubeadm Command 
https://v1-29.docs.kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/

1.sudo kubeadm init \
--pod-network-cidr=192.168.0.0/16 \
--kubernetes-version=1.29.0 \
--control-plane-endpoint=3.81.209.52 (Instance Master IP)

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

You can now join any number of control-plane nodes by copying certificate authorities
and service account keys on each node and then running the following as root:

  kubeadm join 3.81.209.52:6443 --token pv3q3x.4h57psnyp4wsgcbq \
        --discovery-token-ca-cert-hash sha256:a176b9342c255942a1571fa20a894439a5d6985e50272c13e83b0d8fea2dac26 \
        --control-plane 

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 3.81.209.52:6443 --token pv3q3x.4h57psnyp4wsgcbq \
        --discovery-token-ca-cert-hash sha256:a176b9342c255942a1571fa20a894439a5d6985e50272c13e83b0d8fea2dac26 


2. Install calico on Master node
https://kubernetes.io/docs/concepts/cluster-administration/addons/
https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises#install-calico
Select manifests

curl https://raw.githubusercontent.com/projectcalico/calico/v3.29.2/manifests/calico.yaml -O
kubectl apply -f calico.yaml

3. Install KUBEADM on WORKER
sudo swapoff -a

pre-req

cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# sysctl params required by setup, params persist across reboots
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

# Apply sysctl params without reboot
sudo sysctl --system

1. containerd
https://v1-29.docs.kubernetes.io/docs/setup/production-environment/container-runtimes/
https://github.com/containerd/containerd/blob/main/docs/getting-started.md
https://github.com/containerd/containerd/releases?page=2

wget https://github.com/containerd/containerd/releases/download/v1.7.22/containerd-1.7.22-linux-amd64.tar.gz
sudo tar Cxzvf /usr/local containerd-1.7.22-linux-amd64.tar.gz
sudo ln -s /usr/local/bin/containerd /usr/bin/containerd

https://raw.githubusercontent.com/containerd/containerd/main/containerd.service (service file link)

### create systemd file for containerd 
sudo vi /usr/lib/systemd/system/containerd.service

# Copyright The containerd Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target dbus.service

[Service]
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5

# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNPROC=infinity
LimitCORE=infinity

# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this version.
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target
#########################

sudo systemctl daemon-reload
sudo systemctl enable --now containerd

The default configuration can be generated via below command
sudo mkdir -p /etc/containerd/
sudo su
containerd config default > /etc/containerd/config.toml

vi /etc/containerd/config.toml
find SystemdCgroup & change it to true
SystemdCgroup = true
find pause:3.8 and replace with 3.9
registry.k8s.io/pause:3.9

sudo systemctl restart containerd


2. crictl 
https://github.com/kubernetes-sigs/cri-tools/blob/master/docs/crictl.md
https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.29.0/crictl-v1.29.0-linux-amd64.tar.gz

VERSION="v1.29.0" # check latest version in /releases page
wget https://github.com/kubernetes-sigs/cri-tools/releases/download/$VERSION/crictl-$VERSION-linux-amd64.tar.gz
sudo tar zxvf crictl-$VERSION-linux-amd64.tar.gz -C /usr/local/bin

cat <<EOF | sudo tee /etc/crictl.yaml
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
EOF


3. runc
https://github.com/opencontainers/runc/releases

wget https://github.com/opencontainers/runc/releases/download/v1.2.5/runc.amd64
install -m 755 runc.amd64 /usr/local/sbin/runc

4. cni
https://github.com/containernetworking/plugins/releases

wget https://github.com/containernetworking/plugins/releases/download/v1.3.0/cni-plugins-linux-amd64-v1.3.0.tgz
mkdir -p /opt/cni/bin
tar Cxzvf /opt/cni/bin cni-plugins-linux-amd64-v1.3.0.tgz


INSTALL KUBEADM
https://v1-29.docs.kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#installing-kubeadm-kubelet-and-kubectl

1. sudo setenforce 0
2. sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
3. cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.29/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.29/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF

4. Install kubelet, kubeadm and kubectl:
    sudo yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

5. sudo systemctl enable --now kubelet

6. kubeadm join 3.81.209.52:6443 --token pv3q3x.4h57psnyp4wsgcbq \
--discovery-token-ca-cert-hash sha256:a176b9342c255942a1571fa20a894439a5d6985e50272c13e83b0d8fea2dac26

7. Create NGINX POD WITH WELCOME MESSAGE

apiVersion: v1
kind: ConfigMap
metadata:
  name: welcome-page
data:
  index.html: |
    <html>
    <head><title>Welcome to CloudAge</title></head>
    <body>
      <h1>Welcome to CloudAge</h1>
      <h2>Created by Asif Khan</h2>
    </body>
    </html>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: welcome-nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: welcome-nginx
  template:
    metadata:
      labels:
        app: welcome-nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
        volumeMounts:
        - name: welcome-volume
          mountPath: /usr/share/nginx/html
      volumes:
      - name: welcome-volume
        configMap:
          name: welcome-page
---
apiVersion: v1
kind: Service
metadata:
  name: welcome-nginx-service
spec:
  selector:
    app: welcome-nginx
  type: NodePort
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30080  # Change if needed (range: 30000-32767)
