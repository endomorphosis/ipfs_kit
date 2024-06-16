import os
import subprocess
import tempfile
import json
import math
import sys
import time
import random
test_folder = os.path.dirname(os.path.dirname(__file__)) + "/test"
sys.path.append(test_folder)
from .test_fio import test_fio

ipfs_service = """
[Unit]
Description=IPFS Daemon
After=network.target

[Service]
ExecStart=/usr/local/bin/ipfs daemon --enable-gc --enable-pubsub-experiment \"
Restart=on-failure
User=root
Group=root

[Install]
WantedBy=multi-user.target
"""

ipfs_cluster_service = """
[Unit]
Description=IPFS Cluster Daemon
After=network.target

[Service]
ExecStart=/usr/local/bin/ipfs-cluster-service daemon
Restart=on-failure
User=root
Group=root

[Install]
WantedBy=multi-user.target

"""

#NOTE FIX THIS SYSTEMCTL SERVICE

ipfs_cluster_follow = """
[Unit]
Description=IPFS Cluster Follow Daemon
After=network.target

[Service]
ExecStart=/usr/local/bin/ipfs-cluster-follow run
Restart=on-failure
User=root
Group=root

[Install]
WantedBy=multi-user.target

"""


peerlist = """
/ip4/127.0.0.1/tcp/9096/p2p/12D3KooWKw9XCkdfnf8CkAseryCgS3VVoGQ6HUAkY91Qc6Fvn4yv
/ip4/167.99.96.231/tcp/9096/p2p/12D3KooWKw9XCkdfnf8CkAseryCgS3VVoGQ6HUAkY91Qc6Fvn4yv
12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D
/ip4/127.0.0.1/tcp/4001/p2p/12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D
/ip4/127.0.0.1/udp/4001/quic-v1/p2p/12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D
/ip4/127.0.0.1/udp/4001/quic-v1/webtransport/certhash/uEiCQ69lFLNBxmYKhz9pIa6M50fSdJHmgkMnT-Azj4x4jKw/certhash/uEiA0dWNgdbav2huMaLhaX8Aul1n8bOAmNcc3k0HD6Q4juw/p2p/12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D
/ip4/167.99.96.231/tcp/4001/p2p/12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D
/ip4/167.99.96.231/udp/4001/quic-v1/p2p/12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D
/ip4/167.99.96.231/udp/4001/quic-v1/webtransport/certhash/uEiCQ69lFLNBxmYKhz9pIa6M50fSdJHmgkMnT-Azj4x4jKw/certhash/uEiA0dWNgdbav2huMaLhaX8Aul1n8bOAmNcc3k0HD6Q4juw/p2p/12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D
/ip4/167.99.96.231/udp/4001/quic-v1/webtransport/certhash/uEiCQ69lFLNBxmYKhz9pIa6M50fSdJHmgkMnT-Azj4x4jKw/certhash/uEiA0dWNgdbav2huMaLhaX8Aul1n8bOAmNcc3k0HD6Q4juw/p2p/12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D
/ip6/::1/tcp/4001/p2p/12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D
/ip6/::1/udp/4001/quic-v1/p2p/12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D
/ip6/::1/udp/4001/quic-v1/webtransport/certhash/uEiCQ69lFLNBxmYKhz9pIa6M50fSdJHmgkMnT-Azj4x4jKw/certhash/uEiA0dWNgdbav2huMaLhaX8Aul1n8bOAmNcc3k0HD6Q4juw/p2p/12D3KooWS9pEXDb2FEsD"
"""

class install_ipfs:
	def __init__(self, resources, meta=None):
		self.env = {}
		self.env_path = ""
		#NOTE: fix this
		self.this_dir = os.path.dirname(os.path.realpath(__file__))
		self.path = self.path + ":" + os.path.join(self.this_dir, "bin")
		self.path_string = "PATH="+ self.path
		self.ipfs_dist_tar = "https://dist.ipfs.tech/kubo/v0.26.0/kubo_v0.26.0_linux-amd64.tar.gz"
		self.ipfs_follow_dist_tar = "https://dist.ipfs.tech/ipfs-cluster-follow/v1.0.8/ipfs-cluster-follow_v1.0.8_linux-amd64.tar.gz"
		self.ipfs_cluster_dist_tar = "https://dist.ipfs.tech/ipfs-cluster-ctl/v1.0.8/ipfs-cluster-ctl_v1.0.8_linux-amd64.tar.gz"
		self.ipfs_cluster_service_dist_tar = "https://dist.ipfs.tech/ipfs-cluster-service/v1.0.8/ipfs-cluster-service_v1.0.8_linux-amd64.tar.gz"
		self.ipfs_ipget_dist_tar = "https://dist.ipfs.tech/ipget/v0.10.0/ipget_v0.10.0_linux-amd64.tar.gz"
		self.config = None
		self.secret = None
		self.role = None
		self.ipfs_path = None
		self.cluster_name = None
		self.cluster_location = None
		if meta is not None:

			if self.secret == None:
				self.secret = str(random.randbytes(32))
				pass
		
			if "role" in list(meta.keys()):
				self.role = meta['role']
				if self.role not in  ["master","worker","leecher"]:
					raise Exception("role is not either master, worker, leecher")
			else:
				self.role = "leecher"
				pass

			if "ipfs_path" in list(meta.keys()):
				self.ipfs_path = meta['ipfs_path']
				if not os.path.exists(self.ipfs_path):
					os.makedirs(self.ipfs_path)
					pass
				test_disk = test_fio(None)
				self.disk_name = test_disk.disk_device_name_from_location(self.ipfs_path)
				self.disk_stats = {
					"disk_size": test_disk.disk_device_total_capacity(self.disk_name),
					"disk_used": test_disk.disk_device_used_capacity(self.disk_name),
					"disk_avail": test_disk.disk_device_avail_capacity(self.disk_name),
					"disk_name": self.disk_name
				}
				pass
			else:
				if os.geteuid() == 0:
					self.ipfs_path = "/root/.cache/ipfs"
				else:
					self.ipfs_path = os.path.join(os.path.join(os.path.expanduser("~"), ".cache") ,"ipfs" )
				if not os.path.exists(self.ipfs_path):
					os.makedirs(self.ipfs_path)
					pass
				test_disk = test_fio(None)
				self.disk_name = test_disk.disk_device_name_from_location(self.ipfs_path)
				self.disk_stats = {
					"disk_size": test_disk.disk_device_total_capacity(self.disk_name),
					"disk_used": test_disk.disk_device_used_capacity(self.disk_name),
					"disk_avail": test_disk.disk_device_avail_capacity(self.disk_name),
					"disk_name": self.disk_name
				}

			if "cluster_name" in list(meta.keys()):
				self.cluster_name = meta['cluster_name']
				pass					

			if "cluster_location" in list(meta.keys()):
				self.cluster_location = meta['cluster_location']
				pass

			if self.role in ["master","worker","leecher"] and self.ipfs_path is not None:
				self.ipfs_install_command = self.install_ipfs_daemon
				self.ipfs_config_command = self.config_ipfs
				pass

			if self.role == "worker":
				if self.cluster_name is not None and self.ipfs_path is not None:
					self.cluster_install = self.install_ipfs_cluster_follow
					self.cluster_config = self.config_ipfs_cluster_follow
					pass
				pass

			if self.role == "master":
				if self.cluster_name is not None and self.ipfs_path is not None:
					self.cluster_name = meta['cluster_name']
					self.cluster_ctl_install = self.install_ipfs_cluster_ctl
					self.cluster_ctl_config = self.config_ipfs_cluster_ctl
					self.cluster_service_install = self.install_ipfs_cluster_service
					self.cluster_service_config = self.config_ipfs_cluster_service
					pass
				pass

			if "config" in meta:
				if meta['config'] is not None:
					self.config = meta['config']
				
			if "role" in meta:
				if meta['role'] is not None:
					self.role = meta['role']
					if self.role not in  ["master","worker","leecher"]:
						raise Exception("role is not either master, worker, leecher")
					else:
						self.role = meta['role']
						pass
				else:
					self.role = "leecher"

			if "ipfs_path" in meta:
				if meta['ipfs_path'] is not None:
					self.ipfs_path = meta['ipfs_path']
					homedir_path = os.path.expanduser("~")

					#NOTE bug invalid permissions check
					if os.getuid != 0:
						if homedir_path in os.path.realpath(self.ipfs_path):
							if not os.path.exists(os.path.realpath(self.ipfs_path)):
								os.makedirs(self.ipfs_path)
					if os.getuid() == 0:
						if not os.path.exists(self.ipfs_path):
							os.makedirs(self.ipfs_path)
							pass
					#test_disk = test_fio.test_fio(None)
					test_disk = test_fio(None)
					self.disk_name = test_disk.disk_device_name_from_location(self.ipfs_path)
					self.disk_stats = {
						"disk_size": test_disk.disk_device_total_capacity(self.disk_name),
						"disk_used": test_disk.disk_device_used_capacity(self.disk_name),
						"disk_avail": test_disk.disk_device_avail_capacity(self.disk_name),
						"disk_name": self.disk_name
					}
					pass
				pass
			else:
				self.ipfs_path = None
				self.disk_stats = None
				pass

			if "cluster_name" in meta:
				if meta['cluster_name'] is not None:
					self.cluster_name = meta['cluster_name']
					pass
				pass
			else:
				self.cluster_name = None

			if "cluster_location" in meta:
				if meta['cluster_location'] is not None:
					self.cluster_location = meta['cluster_location']
					pass
				pass

			if self.role == "leecher" or self.role == "worker" or self.role == "master":
				if self.ipfs_path is not None: 
					self.ipfs_install_command = self.install_ipfs_daemon
					self.ipfs_config_command = self.config_ipfs
				pass

			if self.role == "worker":
				if self.cluster_name is not None and self.ipfs_path is not None:
					self.cluster_install = self.install_ipfs_cluster_follow
					self.cluster_config = self.config_ipfs_cluster_follow
					pass
				pass

			if self.role == "master":
				if self.cluster_name is not None and self.ipfs_path is not None:
					self.cluster_name = meta['cluster_name']
					self.cluster_ctl_install = self.install_ipfs_cluster_ctl
					self.cluster_ctl_config = self.config_ipfs_cluster_ctl
					self.cluster_service_install = self.install_ipfs_cluster_service
					self.cluster_service_config = self.config_ipfs_cluster_service
					pass
		if "cluster_location"  not in list(self.__dict__.keys()):
			self.cluster_location = "/ip4/167.99.96.231/tcp/9096/p2p/12D3KooWKw9XCkdfnf8CkAseryCgS3VVoGQ6HUAkY91Qc6Fvn4yv"
			pass
		self.bin_path = os.path.join(self.this_dir, "bin")
		self.tmp_path = "/tmp"
	
	def install_ipfs_daemon(self):
		try:
			detect = subprocess.check_output("which ipfs",shell=True)
			detect = detect.decode()
			if len(detect) > 0:
				return True
		except Exception as e:
			detect = 0
			print(e)
		finally:
			pass
		if detect == 0:
			with tempfile.NamedTemporaryFile(suffix=".tar.gz", dir=self.tmp_path) as this_tempfile:
				command = "wget https://dist.ipfs.tech/kubo/v0.26.0/kubo_v0.26.0_linux-amd64.tar.gz -O " + this_tempfile.name
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				command = "tar -xvzf " + this_tempfile.name + " -C " + self.tmp_path
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				if (os.geteuid() == 0):
					#command = "cd /tmp/kubo ; sudo bash install.sh"
					command = "sudo bash " + os.path.join(self.tmp_path, "kubo", "install.sh")
					results = subprocess.check_output(command, shell=True)
					results = results.decode()
					command = "ipfs --version"
					results = subprocess.check_output(command, shell=True)
					results = results.decode()
					with open (os.path.join(self.this_dir, "ipfs.service"), "r") as file:
						ipfs_service = file.read()
					with open("/etc/systemd/system/ipfs.service", "w") as file:
						file.write(ipfs_service)
					command = "systemctl enable ipfs"
					subprocess.call(command, shell=True)
					pass
				else:
					#NOTE: Clean this up and make better logging or drop the error all together
					print('You need to be root to write to /etc/systemd/system/ipfs.service')
					command = 'cd ${self.tmpDir}/kubo && mkdir -p "${thisDir}/bin/" && mv ipfs "${thisDir}/bin/" && chmod +x "${thisDir}/bin/ipfs"'
					results = subprocess.check_output(command, shell=True)
					pass
			command = self.path_string + " ipfs --version"
			results = subprocess.check_output(command, shell=True)
			results = results.decode()
			if "ipfs" in results:
				return True
			else:
				return False
		else:
			return True

	def install_ipfs_cluster_follow(self):
		try:
			detect = subprocess.check_output("which ipfs-cluster-follow",shell=True)
			detect = detect.decode()
			if len(detect) > 0:
				print("ipfs-cluster-follow is already installed.")
				return True
		except Exception as e:
			detect = 0
			print(e)
		finally:
			pass
		if detect == 0:
			with tempfile.NamedTemporaryFile(suffix=".tar.gz", dir=self.tmp_path) as this_tempfile:
				url = self.ipfs_follow_dist_tar
				tar_path = os.path.join("tmp",this_tempfile.name)
				if self.this_dir is not None:
					this_dir = self.this_dir
				else:
					this_dir = os.path.dirname(os.path.realpath(__file__))
					 
				try:
					command = "wget " + url + " -O " + this_tempfile.name
					results = subprocess.check_output(command, shell=True)
					results = results.decode()
					command = "tar -xvzf " + this_tempfile.name + " -C " + self.tmp_path
					results = subprocess.check_output(command, shell=True)
					results = results.decode()
					
					if os.geteuid() == 0:
						with open(os.path.join(this_dir, "ipfs-cluster-follow.service"), "r") as file:
							ipfs_cluster_follow = file.read()
						with open("/etc/systemd/system/ipfs-cluster-follow.service", "w") as file:
							file.write(ipfs_cluster_follow)
						command = "systemctl enable ipfs-cluster-follow"
						results = subprocess.call(command, shell=True)
						# command = "cd /tmp/ipfs-cluster-follow ; sudo mv ipfs-cluster-follow /usr/local/bin/ipfs-cluster-follow"
						command = "sudo mv " + os.path.join(self.tmp_path, "ipfs-cluster-follow",  "ipfs-cluster-follow") + " " + "/usr/local/bin/ipfs-cluster-follow"
						results = subprocess.check_output(command, shell=True)
						results = results.decode()
						pass
					else:
						command = "mv " + os.path.join("/tmp/ipfs-cluster-follow","ipfs-cluster-follow") + " " + os.path.join(self.this_dir , "bin","ipfs-cluster-follow")
						results = subprocess.check_output(command, shell=True)
						results = results.decode()
						pass

				except Exception as e:
					print(e)
					pass

				command = self.path_string + " ipfs-cluster-follow --version"
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				
				if "ipfs-cluster-follow" in results:
					return True
				else:
					return False
	
	def install_ipfs_cluster_ctl(self):
		try:
			detect = subprocess.check_output("which ipfs-cluster-ctl",shell=True)
			detect = detect.decode()
			if len(detect) > 0:
				return True
		except Exception as e:
			detect = 0
			print(e)
		finally:
			pass
			url = self.ipfs_cluster_dist_tar
			with tempfile.NamedTemporaryFile(suffix=".tar.gz", dir=self.tmp_path) as this_tempfile:
				command = "wget " + url + " -O " + this_tempfile.name
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				command = "tar -xvzf " + this_tempfile.name + " -C " + self.tmp_path
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				# command = "cd /tmp/ipfs-cluster-ctl ; sudo mv ipfs-cluster-ctl /usr/local/bin/ipfs-cluster-ctl"
				command = "sudo mv " + os.path.join(self.tmp_path,"ipfs-cluster-ctl","ipfs-cluster-ctl") + " " + " /usr/local/bin/ipfs-cluster-ctl"
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				command = self.path_string + " ipfs-cluster-ctl --version"
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				if "ipfs-cluster-ctl" in results:
					return True
				else:
					return False
	
	def install_ipfs_cluster_service(self):
		try:
			detect = subprocess.check_output("which ipfs-cluster-service",shell=True)
			detect = detect.decode()
			if len(detect) > 0:
				return True
		except Exception as e:
			detect = 0
			print(e)
		finally:
			pass
		if detect == 0:
			with tempfile.NamedTemporaryFile(suffix=".tar.gz", dir=self.tmp_path) as this_tempfile:
				url = self.ipfs_cluster_service_dist_tar
				command = "wget " + url + " -O " + this_tempfile.name
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				command = "tar -xvzf " + this_tempfile.name + " -C /tmp"
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				if os.geteuid() == 0:
					# command = "cd /tmp/ipfs-cluster-service ; sudo mv ipfs-cluster-service /usr/local/bin/ipfs-cluster-service"
					command = "mv " + os.path.join(self.tmp_path ,'ipfs-cluster-service','ipfs-cluster-service') + " " + "/usr/local/bin/ipfs-cluster-service"
					results = subprocess.check_output(command, shell=True)
					results = results.decode()
					with open(os.path.join(self.this_dir, "ipfs-cluster-service.service"), "r") as file:
						ipfs_cluster_service = file.read()
					with open("/etc/systemd/system/ipfs-cluster-service.service", "w") as file:
						file.write(ipfs_cluster_service)
					command = "systemctl enable ipfs-cluster-service"
					subprocess.call(command, shell=True)
				else:
					command = "mv " + os.path.join(self.tmp_path,'ipfs-cluster-service','ipfs-cluster-service') + " " + os.path.join(self.this_dir,"bin","ipfs-cluster-service")
					results = subprocess.check_output(command, shell=True)
					results = results.decode()

				command = self.path_string + " ipfs-cluster-service --version"
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				
				if "ipfs-cluster-service" in results:
					return True
				else:
					return False

	def install_ipget(self):
		try:
			detect = subprocess.check_output("which ipget",shell=True)
			detect = detect.decode()
			if len(detect) > 0:
				return True
		except Exception as e:
			detect = 0
			print(e)
		finally:
			pass
		if detect == 0:
			with tempfile.NamedTemporaryFile(suffix=".tar.gz", dir=self.tmp_path) as this_tempfile:
				url = self.ipfs_ipget_dist_tar
				command = "wget " + url + " -O " + this_tempfile.name
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				command = "tar -xvzf " + this_tempfile.name + " -C " + self.tmp_path
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				# command = "cd /tmp/ipget ; sudo bash install.sh"
				if os.getegid() == 0:
					command = "cd sudo bash " + os.path.join(self.tmp_path, "ipget", "install.sh")
					results = subprocess.check_output(command, shell=True)
					results = results.decode()
					command = "sudo sysctl -w net.core.rmem_max=2500000"
					results = subprocess.check_output(command, shell=True)
					results = results.decode()
					command = "sudo sysctl -w net.core.wmem_max=2500000"
					results = subprocess.check_output(command, shell=True)
					results = results.decode()
				else:
					command = 'cd ' + self.tmp_path + '/ipget && mv ipget "' + self.this_dir + '/bin/" && chmod +x "' + self.this_dir + '/bin/ipget"'
					results = subprocess.call(command, shell=True)
					results = results.decode()

				command = "ipget --version"
				results = subprocess.check_output(command, shell=True)
				results = results.decode()
				if "ipget" in results:
					return True
				else:
					return False

	def config_ipfs_cluster_service(self, **kwargs):
		cluster_name = None
		secret = None
		disk_stats = None
		ipfs_path = None
		
		if "secret" in list(kwargs.keys()):
			secret = kwargs['secret']
		elif "secret" in list(self.__dict__.keys()):
			secret = self.secret
		
		if "cluster_name" in list(kwargs.keys()):
			cluster_name = kwargs['cluster_name']
			self.cluster_name = cluster_name
		elif "cluster_name" in list(self.__dict__.keys()):
			cluster_name = self.cluster_name
		
		
		if "disk_stats" in list(kwargs.keys()):
			disk_stats = kwargs['disk_stats']
			self.disk_stats = disk_stats
		elif "disk_stats" in list(self.__dict__.keys()):
			disk_stats = self.disk_stats

		if "ipfs_path" in list(kwargs.keys()):
			ipfs_path = kwargs['ipfs_path']
			self.ipfs_path = ipfs_path
		elif "ipfs_path" in list(self.__dict__.keys()):
			ipfs_path = self.ipfs_path

		if disk_stats is None:
			raise Exception("disk_stats is None")
		if ipfs_path is None:
			raise Exception("ipfs_path is None")
		if cluster_name is None:
			raise Exception("cluster_name is None")
		if secret is None:
			raise Exception("secret is None")
			
		if "this_dir" in list(self.__dict__.keys()):
			this_dir = self.this_dir
		else:
			this_dir = os.path.dirname(os.path.realpath(__file__))

		home_dir = os.path.expanduser("~")
		ipfs_path = os.path.join(ipfs_path, "ipfs") + "/"
		service_path = ""	
		cluster_path = os.path.join(ipfs_path, cluster_name)
		run_daemon = ""
		init_cluster_daemon_results = ""
		results = {}
		try:
			if os.geteuid() == 0:
				service_path = os.path.join("/root", ".ipfs-cluster")
				pass
			else:
				service_path = os.path.join(os.path.expanduser("~"), ".ipfs-cluster")
				pass
			if cluster_name is not None and ipfs_path is not None and disk_stats is not None:
				if os.geteuid() == 0:
					command0 = "systemctl enable ipfs-cluster-service"
					results0 = subprocess.check_output(command0, shell=True)
					results0 = results0.decode()
					with open(os.path.join(self.this_dir, "service.json"), "r") as file:
						ipfs_cluster_service = file.read()
					with open(service_path + "/service.json", "w") as file:
						file.write(ipfs_cluster_service)
					command1 = "IPFS_PATH="+ ipfs_path +" ipfs-cluster-service init -f"
					results1 = subprocess.check_output(command1, shell=True)
					results1 = results1.decode()
					pass
				else:
					command1 = "IPFS_PATH="+ ipfs_path +" ipfs-cluster-service init -f"
					results1 = subprocess.check_output(command1, shell=True)
					results1 = results1.decode()
					pass
		except Exception as e:
			print(e)
			results1 = str(e)
		finally:
			pass
		results["results1"] = results1
		if (self.role == "worker"):
			try:
				service_config = ""
				workerID = "worker-" + str(random.randbytes(32))
				with open(os.path.join(self.this_dir, "service.json")) as file:
					service_config = json.load(file)
				service_config = service_config.replace('"cluster_name": "ipfs-cluster"', 'cluster_name": "'+cluster_name+'"')				
				service_config = service_config.replace('"secret": "96d5952479d0a2f9fbf55076e5ee04802f15ae5452b5faafc98e2bd48cf564d3"', '"secret": "'+ secret +'"')
				with open(service_path + "/service.json", "w") as file:
					file.write(service_config)	
				with open(os.path.join(this_dir, "peerstore"), "r") as file:
					peerlist = file.read()
				with open(service_path + "/peerstore", "w") as file:
					file.write(peerlist)

				pebble_link = os.path.join(service_path,"pebble")
				pebble_dir = os.path.join(cluster_path, "pebble")

				if cluster_path != service_path:
					if os.path.exists(pebble_link):
						command2 = "rm -rf " + pebble_link
						results2 = subprocess.check_output(command2, shell=True)
						results2 = results2.decode()
						pass
					if not os.path.exists(pebble_dir):
						os.makedirs(pebble_dir)
						pass
					command3 = "ln -s " + pebble_dir + " " + pebble_link
					results3 = subprocess.check_output(command3, shell=True)
					results3 = results3.decode()
					pass

				if os.geteuid() == 0:
					with open(os.path.join(this_dir, "ipfs-cluster.service"), "r") as file:
						service_file = file.read()
					with open("/etc/systemd/system/ipfs-cluster.service", "w") as file:
						file.write(service_file)
					command4 = "systemctl enable ipfs-cluster-serivce"
					results4 = subprocess.check_output(command4, shell=True)
					results4 = results4.decode()
					command5 = "systemctl daemon-reload"
					results5 = subprocess.check_output(command5, shell=True)
					results5 = results5.decode()
					pass
			except Exception as e:
				raise Exception(str(e))
			finally:
				pass
		else:
			try:
				run_daemon_results = ""
				if os.geteuid() == 0:
					reload_daemon = "systemctl daemon-reload"
					reload_daemon_results = subprocess.check_output(reload_daemon, shell=True)
					reload_daemon_results = reload_daemon_results.decode()
					enable_daemon = "systemctl enable ipfs-cluster-service"
					enable_daemon_results = subprocess.check_output(enable_daemon, shell=True)
					enable_daemon_results = enable_daemon_results.decode()
					start_daemon = "systemctl start ipfs-cluster-service"
					start_daemon_results = subprocess.check_output(start_daemon, shell=True)
					start_daemon_results = start_daemon_results.decode()
					time.sleep(5)
					run_daemon = "systemctl status ipfs-cluster-service"
					run_daemon_results = subprocess.check_output(run_daemon, shell=True)
					run_daemon_results = run_daemon_results.decode()
					pass
				else:
					run_daemon_cmd = "ipfs-cluster-service daemon"
					run_daemon_results = subprocess.Popen(run_daemon_cmd, shell=True)
					time.sleep(5)
					run_daemon_results = run_daemon_results.decode()
					if run_daemon is not None:
						results["run_daemon"] = run_daemon_results
					else:
						run_daemon_cmd = "systemctl status ipfs-cluster-service"
						run_daemon_results = subprocess.check_output(run_daemon, shell=True)
						run_daemon_results = run_daemon_results.decode()
						results["run_daemon"] = run_daemon_results
						results2 = run_daemon_results
						pass
					pass

			except Exception as e:
				print(e)
				pass
			finally:
				pass

		return results
	
	def config_ipfs_cluster_ctl(self, **kwargs):
		results = {}

		cluster_name = None
		secret = None
		disk_stats = None
		ipfs_path = None
		
		if "cluster_name" in list(kwargs.keys()):
			cluster_name = kwargs['cluster_name']
			self.cluster_name = cluster_name
		elif "cluster_name" in list(self.__dict__.keys()):
			cluster_name = self.cluster_name
		
		if "disk_stats" in list(kwargs.keys()):
			disk_stats = kwargs['disk_stats']
			self.disk_stats = disk_stats
		elif "disk_stats" in list(self.__dict__.keys()):
			disk_stats = self.disk_stats

		if "ipfs_path" in list(kwargs.keys()):
			ipfs_path = kwargs['ipfs_path']
			self.ipfs_path = ipfs_path
		elif "ipfs_path" in list(self.__dict__.keys()):
			ipfs_path = self.ipfs_path
		
		if "secret" in list(kwargs.keys()):
			secret = kwargs['secret']
			self.secret = secret
		elif "secret" in list(self.__dict__.keys()):
			secret = self.secret

		if disk_stats is None:
			raise Exception("disk_stats is None")
		if ipfs_path is None:
			raise Exception("ipfs_path is None")
		if cluster_name is None:
			raise Exception("cluster_name is None")
		if secret is None:
			raise Exception("secret is None")
		
		run_daemon = None
		run_cluster_ctl = None
		find_daemon_results = 0
		run_ipfs_cluster_service = self.path_string + " ipfs-cluster-service daemon"
		print("Starting ipfs-cluster-service daemon")
		
		results1 = None
		if cluster_name is not None and ipfs_path is not None and disk_stats is not None:
			try:
				command1 = "ipfs-cluster-ctl " + self.cluster_name + " init"
				#results1 = subprocess.check_output(command1, shell=True)
				#results1 = results1.decode()
			except Exception as e:
				#results1 = str(e)
				pass
			finally:
				pass

			try:
				basename = os.path.basename(__file__)
				this_dir = os.path.dirname(__file__)
				homedir = os.path.expanduser("~")
				os.makedirs(ipfs_path+"/" , exist_ok=True)
				os.makedirs(ipfs_path+"/" + "/pebble" , exist_ok=True)
				#os.makedirs(homedir + "/.ipfs-cluster-follow/" + cluster_name , exist_ok=True)
				filename = "service.json"
				dst_file = "service.json"
				#command2 = "cp -rf " + this_dir + "/" + filename + " " + dst_path  + "/" + dst_file
				command3 = "cp -rf " + this_dir + "/" + filename + " ~/.ipfs-cluster/" + dst_file
				filename = "peerstore"
				dst_file = "peerstore"
				#command3 = "cp -rf " + this_dir + "/" + filename + "  ~/.ipfs_cluster-follow/" + dst_file
				command4 = "cp -rf " + this_dir + "/" + filename + "  ~/.ipfs-cluster/" + dst_file
				results3 = subprocess.check_output(command3, shell=True)
				results3 = results3.decode()
				results4 = subprocess.check_output(command4, shell=True)
				results4 = results4.decode()

				if not os.path.exists("~/.ipfs-cluster/pebble"):
					command5 = "rm -rf ~/.ipfs-cluster/pebble ;"
					results5 = subprocess.check_output(command5, shell=True)
					results5 = results5.decode()
					command6 = "ln -s " + ipfs_path + "/pebble ~/.ipfs-cluster/pebble"
					results6 = subprocess.check_output(command6, shell=True)
					results6 = results6.decode()
			except Exception as e:
				results3 = str(e)
				results5 = str(e)
				results4 = str(e)
				results6 = str(e)
			finally:
				pass
			try:
				command5 = " ipfs-cluster-service daemon"
				results5 = subprocess.Popen(command5, shell=True)
			except Exception as e:
				results5 = str(e)
			finally:
				pass
			return {
				"results1":results1
			}

	def config_ipfs_cluster_follow(self, **kwargs):
		if "cluster_name" in list(kwargs.keys()):
			cluster_name = kwargs['cluster_name']
			self.cluster_name = cluster_name
		else:
			cluster_name = self.cluster_name
		if "disk_stats" in list(kwargs.keys()):
			disk_stats = kwargs['disk_stats']
			self.disk_stats = disk_stats
		else:
			disk_stats = self.disk_stats

		if "ipfs_path" in list(kwargs.keys()):
			ipfs_path = kwargs['ipfs_path']
			self.ipfs_path = ipfs_path
		else:
			ipfs_path = self.ipfs_path

		if "disk_stats" not in list(self.__dict__.keys()):
			raise Exception("disk_stats is None")
		else:        
			if self.disk_stats is None:
				raise Exception("disk_stats is None")
		if "ipfs_path" not in list(self.__dict__.keys()):
			raise Exception("ipfs_path is None")
		else:
			if self.ipfs_path is None:
				raise Exception("ipfs_path is None")
		results1 = None
		results2 = None
		ipfs_path = os.path.join(ipfs_path, "ipfs_cluster")          
		self.run_ipfs_daemon()
		if cluster_name is not None and ipfs_path is not None and disk_stats is not None:
			this_dir = os.path.dirname(__file__)
			dst_path = ipfs_path
			try:
				if os.getuid() == 0:
					# Add enabler for ipfs-cluster-follow from the install into the config 
					command0 = "systemctl enable ipfs-cluster-follow"
					results0 = subprocess.check_output(command0, shell=True)

					#command1 = "IPFS_CLUSTER_PATH="+ ipfs_path +" ipfs-cluster-follow ipfs_cluster init " + cluster_name
					command1 = "ipfs-cluster-follow " + cluster_name + " init " + ipfs_path
					results1 = subprocess.check_output(command1, shell=True)
					results1 = results1.decode() 

					# TODO: Add test cases
				else:
					#command1 = "IPFS_CLUSTER_PATH="+ ipfs_path +" ipfs-cluster-follow ipfs_cluster init " + cluster_name
					command1 = "ipfs-cluster-follow " + cluster_name + " init " + ipfs_path
					results1 = subprocess.check_output(command1, shell=True)
					results1 = results1.decode() 

					print('You need to be root to write to /etc/systemd/system/ipfs-cluster-follow.service')				
				
			except Exception as e:
				results1 = str(e)
			finally:
				pass
			try:
				basename = os.path.basename(__file__)
				os.makedirs(ipfs_path+"/" + cluster_name , exist_ok=True)
				os.makedirs(ipfs_path+"/" + cluster_name + "/pebble" , exist_ok=True)
				homedir = os.path.expanduser("~")
				os.makedirs(homedir + "/.ipfs-cluster-follow/" + cluster_name , exist_ok=True)
				filename = "service_follower.json"
				dst_file = "service.json"
				#command2 = "cp -rf " + this_dir + "/" + filename + " " + dst_path  + "/" + dst_file
				command3 = "cp -rf " + this_dir + "/" + filename + " ~/.ipfs-cluster-follow/" + cluster_name + "/" + dst_file
				filename = "peerstore"
				dst_file = "peerstore"
				#command3 = "cp -rf " + this_dir + "/" + filename + "  ~/.ipfs_cluster-follow/" + dst_file
				command4 = "cp -rf " + this_dir + "/" + filename + "  ~/.ipfs-cluster-follow/" + cluster_name + "/" + dst_file
				results3 = subprocess.check_output(command3, shell=True)
				results3 = results3.decode()
				results4 = subprocess.check_output(command4, shell=True)
				results4 = results4.decode()

				if not os.path.exists("~/.ipfs-cluster-follow/"+ cluster_name + "/pebble"):
					command5 = "rm -rf ~/.ipfs-cluster-follow/" + cluster_name + "/pebble ;"
					results5 = subprocess.check_output(command5, shell=True)
					results5 = results5.decode()
					command6 = "ln -s " + ipfs_path + "/" + cluster_name + "/pebble ~/.ipfs-cluster-follow/" + cluster_name + "/pebble"
					results6 = subprocess.check_output(command6, shell=True)
					results6 = results6.decode()
			except Exception as e:
				results3 = str(e)
				results5 = str(e)
				results4 = str(e)
				results2 = str(e)
				results6 = str(e)
			finally:
				pass
			try:
				command4 = "IPFS_CLUSTER_PATH="+ ipfs_path +" ipfs-cluster-follow " + cluster_name + " run"
				command5 = "ipfs-cluster-follow " + cluster_name + " run"
				results5 = subprocess.Popen(command5, shell=True)
			except Exception as e:
				results5 = str(e)
			finally:
				pass
			new_ipfs_cluster_follow = ipfs_cluster_follow.replace("run"," "+ cluster_name + " run")
			
			if os.geteuid() == 0:
				with open("/etc/systemd/system/ipfs-cluster-follow.service", "w") as file:
					file.write(new_ipfs_cluster_follow)
			else:
				#NOTE: Clean this up and make better logging or drop the error all together
				print('You need to be root to write to /etc/systemd/system/ipfs-cluster-follow.service')
			
			# TODO: Add test cases to all the config functions

			#command = "ps -ef | grep ipfs | grep -v grep | awk '{print $2}' | xargs kill -9"
			#results = subprocess.run(command, shell=True)
			results = {
				"results1":results1,
				"results2":results2,
				"results3":results3,
				"results4":results4,
				"results5":results5,
				"results6":results6
			}

			return results
					
	def config_ipfs(self, **kwargs):
		if "disk_stats" in list(kwargs.keys()):
			disk_stats = kwargs['disk_stats']
			self.disk_stats = disk_stats
		else:
			disk_stats = self.disk_stats

		if "ipfs_path" in list(kwargs.keys()):
			ipfs_path = kwargs['ipfs_path']
			self.ipfs_path = ipfs_path
		else:
			ipfs_path = self.ipfs_path

		if "disk_stats" not in list(self.__dict__.keys()):
			raise Exception("disk_stats is None")
		else:        
			if self.disk_stats is None:
				raise Exception("disk_stats is None")
		if "ipfs_path" not in list(self.__dict__.keys()):
			raise Exception("ipfs_path is None")
		else:
			if self.ipfs_path is None:
				raise Exception("ipfs_path is None")

		if ipfs_path[-1] != "/":
			ipfs_path = ipfs_path + "/ipfs/"
		else:
			ipfs_path = ipfs_path + "ipfs/"

		os.makedirs(ipfs_path, exist_ok=True)
		if disk_stats is not None and ipfs_path is not None and disk_stats is not None:
			try:
				command1 = "IPFS_PATH="+ ipfs_path +" ipfs init --profile=badgerds"
				results1 = subprocess.check_output(command1, shell=True)
				results1 = results1.decode()
			except Exception as e:
				results1 = str(e)
			finally:
				pass
			try:
				command2 = "IPFS_PATH="+ ipfs_path +" ipfs id "
				results2 = subprocess.check_output(command2, shell=True)
				results2 = results2.decode()
				peer_id = results2
			except Exception as e:
				results2 = str(e)
			try:
				command4 = "IPFS_PATH="+ ipfs_path + " ipfs config profile apply badgerds"
				results4 = subprocess.check_output(command4, shell=True)
				results4 = results4.decode()
			except Exception as e:
				results4 = str(e)
			finally:
				pass
			min_free_space = 32 * 1024 * 1024 * 1024
			disk_available = self.disk_stats['disk_avail']
			if "T" in disk_available:
				disk_available = float(disk_available.replace("T","")) * 1024 * 1024 * 1024 * 1024
			elif "G" in disk_available:
				disk_available = float(disk_available.replace("G","")) * 1024 * 1024 * 1024
			elif "M" in disk_available:
				disk_available = float(disk_available.replace("M","")) * 1024 * 1024

			if disk_available > min_free_space:
				allocate = math.ceil((( disk_available - min_free_space) * 0.8) / 1024 / 1024 / 1024)
				try:
					command5 = "IPFS_PATH="+ ipfs_path +" ipfs config Datastore.StorageMax " + str(allocate) + "GB"
					results5 = subprocess.check_output(command5, shell=True)
					results5 = results5.decode()
				except Exception as e:
					results5 = str(e)
				finally:
					pass
			else:
				results5 = "disk_available is less than min_free_space"
			basedir = os.path.dirname(__file__)
			with open(basedir + "/peerstore", "r") as file:
				peerlist = file.read()
			peerlist = peerlist.split("\n")
			for peer in peerlist:
				if peer != "":
					try:
						command6 = "IPFS_PATH="+ ipfs_path + " ipfs bootstrap add " + peer
						# TODO: Permission error on the config when installing as user
						results6 = subprocess.check_output(command6, shell=True)
						results6 = results6.decode()
					except Exception as e:
						results6 = str(e)
					finally:
						pass
			try:
				command7 = "IPFS_PATH="+ ipfs_path + " ipfs init"
				results7 = subprocess.Popen(command7, shell=True)
			except Exception as e:
				results7 = str(e)
			finally:
				pass

			if os.geteuid() == 0:
				ipfs_service_text = ipfs_service.replace("ExecStart=","ExecStart= bash -c \"export IPFS_PATH="+ ipfs_path + " && ")
				with open("/etc/systemd/system/ipfs.service", "w") as file:
					file.write(ipfs_service_text)

				try:
					# Reload daemon
					command11 = "systemctl daemon-reload"
					results11 = subprocess.Popen(command11, shell=True)
					
					# Enable service 
					command0 = "systemctl enable ipfs"
					results0 = subprocess.Popen(command0, shell=True)

					# Start daemon
					command22 = "systemctl start ipfs"
					results22 = subprocess.Popen(command22, shell=True)

					# Check if daemon is running
					command3 = "ps -ef | grep ipfs | grep daemon | grep -v grep | wc -l"
					results3 = subprocess.check_output(command3, shell=True)
					results3 = results3.decode()

					if(int(results3) > 0):
							# Downloads image from ipfs as a test
							command5 = "bash -c \"export IPFS_PATH="+ ipfs_path + " && ipfs cat /ipfs/QmSgvgwxZGaBLqkGyWemEDqikCqU52XxsYLKtdy3vGZ8uq >" + ipfs_path + "/test.jpg \" " 
							results5 = subprocess.Popen(command5, shell=True)

							# Time out for 2 seconds to allow the file to download
							time.sleep(5)	 

							if os.path.exists(ipfs_path + "/test.jpg"):
								if os.path.getsize(ipfs_path + "/test.jpg") > 0:
									# Remove the test file
									pass
								else:
									raise Exception("ipfs failed to download test file")
							
							os.remove(ipfs_path + "/test.jpg")
								
					else:
						raise Exception("ipfs failed to download test file")
			
				except Exception as e:
					# Should this return an error or log it like line 673
					return str(e)

				finally:
					command6 = "systemctl stop ipfs"
					results6 = subprocess.Popen(command6, shell=True)

			else:
				#NOTE: Not sure if this needs to logged or excepted 
				print('You need to be root to write to /etc/systemd/system/ipfs.service')

			if "exit" not in results1:
				identity = results1.split("\n")
				identity = identity[1].replace("peer identity: ","").strip()
			ipfs_id = json.loads(results2)
			identity = ipfs_id['ID']
			public_key = ipfs_id['PublicKey']
			config = json.loads(results4) 
			#ipfs_daemon = results7 
			results = {
				"config":config,
				"identity":identity,
				"public_key":public_key,
#                "ipfs_daemon":ipfs_daemon
			}
			return results
		
	def run_ipfs_cluster_service(self, **kwargs):
		if "ipfs_path" in list(kwargs.keys()):
			ipfs_path = kwargs['ipfs_path']
		else:
			ipfs_path = self.ipfs_path

		ipfs_path = ipfs_path + "ipfs/"
		os.makedirs(ipfs_path, exist_ok=True)

		command = "IPFS_CLUSTER_PATH="+ self.ipfs_path +" ipfs-cluster-service"
		results = subprocess.Popen(command, shell=True)
		return results
	
	def run_ipfs_cluster_ctl(self, **kwargs):
		if "ipfs_path" in list(kwargs.keys()):
			ipfs_path = kwargs['ipfs_path']
			ipfs_path = ipfs_path + "ipfs/"
			os.makedirs(ipfs_path, exist_ok=True)
		else:
			ipfs_path = self.ipfs_path          
			ipfs_path = ipfs_path + "ipfs/"
			os.makedirs(ipfs_path, exist_ok=True)

		command = "IPFS_CLUSTER_PATH="+ self.ipfs_path +"/ipfs/ ipfs-cluster-ctl"
		results = subprocess.Popen(command, shell=True)
		return results
	
	def run_ipfs_cluster_follow(self, **kwargs):
		if "ipfs_path" in list(kwargs.keys()):
			ipfs_path = kwargs['ipfs_path']
			ipfs_path = ipfs_path + "ipfs/"
			os.makedirs(ipfs_path, exist_ok=True)
		else:
			ipfs_path = self.ipfs_path          
			ipfs_path = ipfs_path + "ipfs/"
			os.makedirs(ipfs_path, exist_ok=True)
		try:
			command7 = "IPFS_PATH="+ ipfs_path + "/ipfs/ ipfs daemon --enable-pubsub-experiment"
			results7 = subprocess.Popen(command7, shell=True)
		except Exception as e:
			results7 = str(e)
		finally:
			pass
		return results7
	
	def run_ipfs_daemon(self, **kwargs):
		if "ipfs_path" in list(kwargs.keys()):
			ipfs_path = kwargs['ipfs_path']
		else:
			ipfs_path = self.ipfs_path

		if ipfs_path[-1] != "/":
			ipfs_path = ipfs_path + "/ipfs/"
		else:
			ipfs_path = ipfs_path + "ipfs/"
		os.makedirs(ipfs_path, exist_ok=True)

		try:
			command7 = "IPFS_PATH="+ ipfs_path + " ipfs daemon --enable-pubsub-experiment"
			results7 = subprocess.Popen(command7, shell=True)
		except Exception as e:
			results7 = str(e)
		finally:
			pass
	
		return results7
	
	def uninstall_ipfs(self):
		try:
			command = "ps -ef | grep ipfs | grep daemon | grep -v grep | awk '{print $2}' | xargs kill -9"
			results = subprocess.run(command, shell=True)

			command = "which ipfs"
			results = subprocess.check_output(command, shell=True)
			results = results.decode()

			command = "sudo rm " + results
			results = subprocess.check_output(command, shell=True)
			
			command = "sudo rm -rf " + self.ipfs_path
			results = subprocess.check_output(command, shell=True)

			command = "sudo rm -rf /etc/systemd/system/ipfs.service"
			results = subprocess.check_output(command, shell=True)
			
			return True
		except Exception as e:
			results = str(e)
			return False
		finally:
			pass

	def uninstall_ipfs_cluster_service(self):
		# TODO: This needs to be tested
		try:
			command = "ps -ef | grep ipfs-cluster-service | grep -v grep | awk '{print $2}' | xargs kill -9"
			results = subprocess.run(command, shell=True)
			
			command = "which ipfs-cluster-service"
			results = subprocess.check_output(command, shell=True)
			results = results.decode()
			
			command = "sudo rm " + results
			results = subprocess.check_output(command, shell=True)
			
			command = "sudo rm -rf ~/.ipfs-cluster"
			results = subprocess.check_output(command, shell=True)

			command = "sudo rm -rf /etc/systemd/system/ipfs-cluster-service.service"
			results = subprocess.check_output(command, shell=True)
			
			return True
		except Exception as e:
			results = str(e)
			return False
		finally:
			pass



	def uninstall_ipfs_cluster_follow(self):
		try:
			command = "ps -ef | grep  ipfs-cluster-follow | grep -v grep | awk '{print $2}' | xargs kill -9"
			results = subprocess.run(command, shell=True)
			
			command = "which ipfs-cluster-follow"
			results = subprocess.check_output(command, shell=True)
			results = results.decode()
			
			command = "sudo rm " + results
			results = subprocess.check_output(command, shell=True)
			
			command = "sudo rm -rf ~/.ipfs-cluster-follow"
			results = subprocess.check_output(command, shell=True)

			command = "sudo rm -rf /etc/systemd/system/ipfs-cluster-follow.service"
			results = subprocess.check_output(command, shell=True)

			return True
		
		except Exception as e:
			results = str(e)
			return False
		finally:
			pass


	def uninstall_ipfs_cluster_ctl(self):
		try:
			command = "ps -ef | grep ipfs-cluster-ctl | grep -v grep | awk '{print $2}' | xargs kill -9"
			results = subprocess.run(command, shell=True)

			command = "which ipfs-cluster-ctl"
			results = subprocess.check_output(command, shell=True)
			results = results.decode()

			command = "sudo rm " + results
			results = subprocess.check_output(command, shell=True)
			
			return True
		except Exception as e:
			results = str(e)
			return False
		finally:
			pass

	def uninstall_ipget(self):
		try:
			command = "ps -ef | grep ipget | grep -v grep | awk '{print $2}' | xargs kill -9"
			results = subprocess.run(command, shell=True)

			command = "which ipget"
			results = subprocess.check_output(command, shell=True)
			results = results.decode()

			command = "sudo rm " + results
			results = subprocess.check_output(command, shell=True)
			
			return True
		except Exception as e:
			results = str(e)
			return False
		finally:
			pass
	
	def test_uninstall(self):
		if self.role == "leecher" or self.role == "worker" or self.role == "master":
			ipfs = self.uninstall_ipfs()
			ipget = self.uninstall_ipget()
			pass
		if self.role == "master":
			cluster_service  = self.uninstall_ipfs_cluster_service()
			cluster_ctl = self.uninstall_ipfs_cluster_ctl()
			pass
		if self.role == "worker":
			cluster_follow = self.uninstall_ipfs_cluster_follow()
			pass

	def install_executables(self, **kwargs):
		results = {}
		if self.role == "leecher" or self.role == "worker" or self.role == "master":
			ipfs = self.install_ipfs_daemon()
			results["ipfs"] = ipfs
		pass
		if self.role == "master":
			cluster_service  = self.install_ipfs_cluster_service()
			cluster_ctl = self.install_ipfs_cluster_ctl()
			results["cluster_service"] = cluster_service
			results["cluster_ctl"] = cluster_ctl
			pass
		if self.role == "worker":
			cluster_follow = self.install_ipfs_cluster_follow()
			results["cluster_follow"] = cluster_follow
			pass
		return results
	
	def config_executables(self, **kwargs):
		results = {}
		if self.role == "leecher" or self.role == "worker" or self.role == "master":
			ipfs_config = self.config_ipfs(cluster_name = self.cluster_name, ipfs_path = self.ipfs_path)
			results["ipfs_config"] = ipfs_config["config"]
			pass
		if self.role == "master":
			cluster_service_config = self.config_ipfs_cluster_service(cluster_name = self.cluster_name, ipfs_path = self.ipfs_path)
			cluster_ctl_config = self.config_ipfs_cluster_ctl(cluster_name = self.cluster_name, ipfs_path = self.ipfs_path)
			results["cluster_service_config"] = cluster_service_config
			results["cluster_ctl_config"] = cluster_ctl_config
			pass
		if self.role == "worker":
			cluster_follow_config = self.config_ipfs_cluster_follow(cluster_name = self.cluster_name, ipfs_path =  self.ipfs_path)
			results["cluster_follow_config"] = cluster_follow_config
			pass
		return results
	
	def ipfs_test_install(self):
		detect = os.system("which ipfs")
		if len(detect) > 0:
			return True
		else:
			return False
		pass

	def ipfs_cluster_service_test_install(self):
		detect = os.system("which ipfs-cluster-service")
		if len(detect) > 0:
			return True
		else:
			return False
		pass

	def ipfs_cluster_follow_test_install(self):
		detect = os.system("which ipfs-cluster-follow")
		if len(detect) > 0:
			return True
		else:
			return False
		pass

	def ipfs_cluster_ctl_test_install(self):
		detect = os.system("which ipfs-cluster-ctl")
		if len(detect) > 0:
			return True
		else:
			return False
		pass

	def ipget_test_install(self):
		detect = os.system("which ipget")
		if len(detect) > 0:
			return True
		else:
			return False
		pass


	def install_config(self, **kwargs):
		results = {}
		if self.role == "leecher" or self.role == "worker" or self.role == "master":
			ipget = self.install_ipget()
			ipfs = self.install_ipfs_daemon()
			ipfs_config = self.config_ipfs(cluster_name = self.cluster_name, ipfs_path = self.ipfs_path)
			# NOTE: This fails some times but never when debugging so probably some sort of race issue 
			results["ipfs"] = ipfs
			results["ipfs_config"] = ipfs_config["config"]
			self.run_ipfs_daemon()
			pass
		if self.role == "master":
			cluster_service  = self.install_ipfs_cluster_service()
			cluster_ctl = self.install_ipfs_cluster_ctl()
			cluster_service_config = self.config_ipfs_cluster_service(cluster_name = self.cluster_name, ipfs_path = self.ipfs_path)
			cluster_ctl_config = self.config_ipfs_cluster_ctl(cluster_name = self.cluster_name, ipfs_path = self.ipfs_path)
			results["cluster_service"] = cluster_service
			results["cluster_ctl"] = cluster_ctl
			results["cluster_service_config"] = cluster_service_config
			results["cluster_ctl_config"] = cluster_ctl_config
			pass
		if self.role == "worker":
			cluster_follow = self.install_ipfs_cluster_follow()
			cluster_follow_config = self.config_ipfs_cluster_follow(cluster_name = self.cluster_name, ipfs_path =  self.ipfs_path)
			results["cluster_follow"] = cluster_follow
			results["cluster_follow_config"] = cluster_follow_config
			pass

		# NOTE: Check if this runs and completes successfully
		systemctl_reload = "systemctl daemon-reload"
		results["systemctl_reload"] = subprocess.run(systemctl_reload, shell=True)

		return results

if __name__ == "__main__":
	meta = {
		"role":"worker",
		"cluster_name":"cloudkit_storage",
		"cluster_location":"/ip4/167.99.96.231/tcp/9096/p2p/12D3KooWKw9XCkdfnf8CkAseryCgS3VVoGQ6HUAkY91Qc6Fvn4yv",
		#"cluster_location": "/ip4/167.99.96.231/udp/4001/quic-v1/p2p/12D3KooWS9pEXDb2FEsDv9TH4HicZgwhZtthHtSdSfyKKDnkDu8D",
		"config":None,
		"ipfs_path":"/home/kensix/.cache/ipfs",
	}
	install = install_ipfs(None, meta=meta) 
	# results = install.test_uninstall()
	
	results = install.install_config()

	print(results)
	pass
