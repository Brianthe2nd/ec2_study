#!/usr/bin/env python3
import subprocess
import boto3
import time
import os
import paramiko
import sys 

PARTS_DIR = "parts"
BRANCH = "main"
AWS_REGION = "eu-north-1"
AMI_ID = "ami-0c4fc5dcabc9df21d"
INSTANCE_TYPE = "c7i-flex.large"
KEY_NAME = "my_c71"
SSH_KEY_FILE = os.path.expanduser("C:/Users/Brayo/Downloads/my_c71.pem")
SEC_GROUP_NAME = "allow-ssh-from-me"
INSTANCE_USER = "ec2-user"

ec2 = boto3.client("ec2", region_name=AWS_REGION)

def run(cmd):
    print(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def ensure_security_group():
    """Ensure a security group exists that allows SSH."""
    groups = ec2.describe_security_groups(Filters=[{"Name":"group-name","Values":[SEC_GROUP_NAME]}])
    if groups["SecurityGroups"]:
        return groups["SecurityGroups"][0]["GroupId"]

    sg = ec2.create_security_group(
        GroupName=SEC_GROUP_NAME,
        Description="Allow SSH"
    )
    sg_id = sg["GroupId"]
    my_ip = subprocess.check_output("curl -s https://checkip.amazonaws.com", shell=True).decode().strip()
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            "IpProtocol":"tcp","FromPort":22,"ToPort":22,
            "IpRanges":[{"CidrIp":f"{my_ip}/32"}]
        }]
    )
    return sg_id

# def ensure_security_group():
#     """Ensure a security group exists that allows SSH from all IPs."""
#     groups = ec2.describe_security_groups(Filters=[{"Name": "group-name", "Values": [SEC_GROUP_NAME]}])
#     if groups["SecurityGroups"]:
#         return groups["SecurityGroups"][0]["GroupId"]

#     sg = ec2.create_security_group(
#         GroupName=SEC_GROUP_NAME,
#         Description="Allow SSH from anywhere"
#     )
#     sg_id = sg["GroupId"]

#     ec2.authorize_security_group_ingress(
#         GroupId=sg_id,
#         IpPermissions=[{
#             "IpProtocol": "tcp",
#             "FromPort": 22,
#             "ToPort": 22,
#             "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
#         }]
#     )
#     return sg_id


def launch_instance(sg_id):
    resp = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=[sg_id],
        MinCount=1, MaxCount=1,
        BlockDeviceMappings=[
            {
                "DeviceName": "/dev/xvda",  # root volume
                "Ebs": {
                    "VolumeSize": 20,        # 20 GB
                    "VolumeType": "gp3",     # gp3 is cheap general purpose
                    "DeleteOnTermination": True
                }
            }
        ]
    )
    instance = resp["Instances"][0]
    instance_id = instance["InstanceId"]

    print(f"Launched instance {instance_id}, waiting...")
    ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])

    # get public ip
    desc = ec2.describe_instances(InstanceIds=[instance_id])
    ip = desc["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    return instance_id, ip



def ssh_and_fetch(ip):
    key = paramiko.RSAKey.from_private_key_file(SSH_KEY_FILE)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {ip} ...")
    ssh.connect(ip, username=INSTANCE_USER, pkey=key , banner_timeout=200)
    transport = ssh.get_transport()

    if transport and transport.is_active():
        print("Paramiko client is connected to the SSH server.")
    else:
        print("Paramiko client is NOT connected to the SSH server.")
        return

    # upload ssh_fetch.sh
    sftp = ssh.open_sftp()
    remote_path = f"/home/{INSTANCE_USER}/ssh_fetch.sh"
    sftp.put("ssh_fetch.sh", remote_path)
    sftp.close()

    # make executable
    ssh.exec_command(f"chmod +x {remote_path}")

    # run script
    stdin, stdout, stderr = ssh.exec_command(remote_path)

    # stream script output
    for line in iter(stdout.readline, ""):
        sys.stdout.write(line)
        sys.stdout.flush()

    err = stderr.read().decode()
    if err:
        print("Errors:\n", err)

    # ✅ wait until main.py is running
    print("Checking if main.py started...")
    started = False
    for _ in range(30):  # check up to 30 times (30s max)
        stdin, stdout, stderr = ssh.exec_command("pgrep -f driver.py")
        pid = stdout.read().decode().strip()
        if pid:
            print(f"main.py is running with PID {pid}")
            started = True
            break
        time.sleep(1)

    if not started:
        print("main.py did not start within 30 seconds.")
        ssh.close()
        return

    # for _ in range(10):
    #     stdin, stdout, stderr = ssh.exec_command("test -f main.log && echo OK")
    #     if stdout.read().decode().strip() == "OK":
    #         print("main.log found, starting to stream logs...")
    #         break
    #     time.sleep(1)
    # else:
    #     print("main.log not created within 30s")
    #     return

    # # stream the log
    # stdin, stdout, stderr = ssh.exec_command("tail -f main.log")
    # try:
    #     for line in iter(stdout.readline, ""):
    #         sys.stdout.write(line)
    #         sys.stdout.flush()
    # except KeyboardInterrupt:
    #     print("\nStopped log streaming.")


def main():
    sg_id = ensure_security_group()

    for part in sorted(os.listdir(PARTS_DIR)):
        if not part.endswith(".csv"): continue
        # part_path = os.path.join(PARTS_DIR, part)
        # part_path = PARTS_DIR + "/" + part
        part_path = os.path.abspath(os.path.join(PARTS_DIR, part))

        

        print(f"=== Processing {part} ===")
        run(f"bash git_update.sh {part_path}")

        inst_id, ip = launch_instance(sg_id)
        print(f"Instance {inst_id} with IP {ip}")

        # wait a bit for sshd
        time.sleep(30)
        ssh_and_fetch(ip)

if __name__ == "__main__":
    main()
