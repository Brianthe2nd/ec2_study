import boto3
import paramiko
import os

def stop_driver_on_unnamed_instances(region="us-east-1", key_file="~/.ssh/id_rsa", username="ec2-user", script_path="stop_driver.sh"):
    """
    Finds all running EC2 instances without a Name tag,
    uploads a shell script, and executes it.
    """
    ec2 = boto3.client("ec2", region_name=region)

    reservations = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )["Reservations"]

    for reservation in reservations:
        for instance in reservation["Instances"]:
            # Skip instances with a Name tag
            tags = instance.get("Tags", [])
            has_name = any(tag["Key"] == "Name" for tag in tags)
            if has_name:
                continue

            public_ip = instance.get("PublicIpAddress")
            if not public_ip:
                print(f"Skipping {instance['InstanceId']} (no public IP)")
                continue

            print(f"Connecting to {instance['InstanceId']} ({public_ip})...")

            try:
                key = paramiko.RSAKey.from_private_key_file(os.path.expanduser(key_file))
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(public_ip, username=username, pkey=key)

                # Upload script
                sftp = ssh.open_sftp()
                remote_path = "/tmp/stop_driver.sh"
                sftp.put(script_path, remote_path)
                sftp.chmod(remote_path, 0o755)
                sftp.close()

                # Execute script
                stdin, stdout, stderr = ssh.exec_command(f"bash {remote_path}")
                print(f"Output from {instance['InstanceId']}: {stdout.read().decode()}")
                print(f"Errors from {instance['InstanceId']}: {stderr.read().decode()}")

                ssh.close()
            except Exception as e:
                print(f"Failed to connect to {instance['InstanceId']} ({public_ip}): {e}")


stop_driver_on_unnamed_instances(
    region="eu-north-1", 
    key_file="C://users/Brayo/Downloads/my_c71.pem", 
    # "C:/Users/Brayo/Downloads/my_c71.pem"
    username="ec2-user"
)
