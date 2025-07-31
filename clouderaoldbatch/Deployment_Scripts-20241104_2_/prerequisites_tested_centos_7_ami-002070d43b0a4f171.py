from subprocess import call

job_list = [
'sudo yum install wget -y',
'sudo yum install nano -y',
'wget https://s3.amazonaws.com/cloud-age/jdk-8u162-linux-x64.rpm',
'sudo rpm -Uv jdk-8u162-linux-x64.rpm',
'wget https://s3.amazonaws.com/cloud-age/MIT_kerberos/prerequisite/check-pre-req.sh',
'wget https://s3.amazonaws.com/cloud-age/MIT_kerberos/prerequisite/disable_iptables.sh',
'wget https://s3.amazonaws.com/cloud-age/MIT_kerberos/prerequisite/disable_ipv6.sh',
'wget https://s3.amazonaws.com/cloud-age/MIT_kerberos/prerequisite/disable_selinux.sh',
'wget https://s3.amazonaws.com/cloud-age/MIT_kerberos/prerequisite/disable_thp.sh',
'wget https://s3.amazonaws.com/cloud-age/MIT_kerberos/prerequisite/install_lzo.sh',
'wget https://s3.amazonaws.com/cloud-age/MIT_kerberos/prerequisite/install_nscd.sh',
'wget https://s3.amazonaws.com/cloud-age/MIT_kerberos/prerequisite/install_tools.sh',
'wget https://s3.amazonaws.com/cloud-age/MIT_kerberos/prerequisite/remove_tuned.sh',
'wget https://s3.amazonaws.com/cloud-age/MIT_kerberos/prerequisite/tune_kernel.sh',
'sudo sh disable_iptables.sh',
'sudo sh disable_ipv6.sh',
'sudo sh disable_selinux.sh',
'sudo sh disable_thp.sh',
'sudo sh install_lzo.sh',
'sudo sh install_nscd.sh',
'sudo sh install_tools.sh',
'sudo sh remove_tuned.sh',
'sudo sh tune_kernel.sh',
'sudo yum install ntp ntpdate ntp-doc -y',
'sudo chkconfig ntpd on',
'sudo systemctl start ntpd',
'sudo sysctl -a | grep vm.swappiness',
"""sudo su -c 'cat >>/etc/sysctl.conf <<EOL
'vm.swappiness=1'
EOL'""",
'sudo sysctl -p',
"sudo sed -i '/exit 0/d' /etc/rc.local",
"""sudo su -c 'cat >>/etc/rc.local <<EOL
if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
  echo never > /sys/kernel/mm/transparent_hugepage/enabled
fi
if test -f /sys/kernel/mm/transparent_hugepage/defrag; then
   echo never > /sys/kernel/mm/transparent_hugepage/defrag 
fi
exit 0
EOL'""",
'sudo yum install sssd -y',
'wget https://mycloudage.s3.ap-south-1.amazonaws.com/sssd.conf',
'sudo mv sssd.conf /etc/sssd/',
'sudo chown root:root /etc/sssd/sssd.conf',
'sudo chmod 600 /etc/sssd/sssd.conf',
'sudo systemctl enable sssd',
'sudo systemctl start sssd',
'sudo authconfig --enablesssdauth --enablesssd --updateall',
'wget https://mycloudage.s3.ap-south-1.amazonaws.com/nscd.conf',
'sudo mv nscd.conf /etc/',
'sudo timedatectl set-ntp true',
'sudo timedatectl status',
'sudo service postfix restart',
'sudo systemctl start chronyd',
'sudo systemctl enable chronyd',
"""sudo su -c touch /home/centos/.ssh/config; echo -e \ "Host *\n StrictHostKeyChecking no\n UserKnownHostsFile=/dev/null" \ > ~/.ssh/config""",
"""echo -e 'y\n'| ssh-keygen -t rsa -P "" -f $HOME/.ssh/id_rsa""",
'cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys',
'sudo chmod 600 config',
'wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.46.tar.gz',
'tar zxvf mysql-connector-java-5.1.46.tar.gz',
'sudo mkdir -p /usr/share/java/',
'sudo cp mysql-connector-java-5.1.46/mysql-connector-java-5.1.46-bin.jar /usr/share/java/mysql-connector-java.jar',
'wget https://dev.mysql.com/get/mysql57-community-release-el7-9.noarch.rpm',
'md5sum mysql57-community-release-el7-9.noarch.rpm',
'sudo rpm -ivh mysql57-community-release-el7-9.noarch.rpm',
'sudo yum install --nogpgcheck mysql-server -y',
'sh check-pre-req.sh',
]

for job in job_list:    
    call(job, shell=True)





