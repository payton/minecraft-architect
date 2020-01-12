# Minecraft Architect
***Reimagine The Good Place (or The Bad Place) in Minecraft. Become your own architect and manifest a world where it's your way or the highway. Design a server for who you want no matter what Chidi says is 'ethical' or not.***

## Summary
An AWS-hosted Minecraft server that you only pay for when it's being used. Minecraft Architect utilizes AWS EC2 and Heroku to start the server at will and automatically shut it down when idle. This project is based on/adapted from trevor/OnDemandMinecraft and utilizes alternative methods of server startup and cron jobs.

## Setup

#### Prerequisites
* Amazon AWS Account
* Familiarity with SSH, Linux, AWS, and Git
* Cloned this repository

#### AWS Configuration
1. IAM User
    1. Go to the `IAM Management Console`, select `Users` on the left and `Add user` 
    1. Create a username and select the `Programmatic Access` box
    1. Assign the user to a new group with `AmazonEC2FullAccess`
    1. Continue through the new user wizard and create user (no further configuration is vital at this point)
    1. Take note of the `Access key ID` and `Secret access key` - these will be used later
1. EC2 Key Pair
    1. Go to the `EC2 Management Console`, select `Key Pairs` under `Network & Security` in the left sidebar
    1. Select `Create Key Pair` and name it as desired
    2. Save the resulting `.pem` file - this should prompt you automatically
3. CloudFormation (the magic)
    1. Go to `CloudFormation`, select `Create stack` and continue with the `with new resources (standard)` option
    1. Use the `Upload a template file` option and upload the `instance/infrastructure.yaml` file in this respository
    1. Follow the construction wizard (see tips below)
        * When choosing your AMI, you will need to select one in your current AWS region, with amd64 Arch type, hvm:ebs instance type, and I suggest Ubuntu 16.04 or above in order to have Java 8 available to you. This filter `us-east-2 amd64 hvm:ebs` will help narrow down your options (note you must change the region)
        * Your instance type will be trial and error and will change the running costs of the server. I use a `t3.small` size with a 20 person server but have not yet reached capacity. See instance specs here https://aws.amazon.com/ec2/instance-types/t3/
        * The key name is the name of our key pair created in the last section. This should appear in the drop down menu automatically.
        * If you would like anyone to SSH into your instance, leave the SSHLocation as is. If not, place your IP in this location. You must include a range. If your IP is `192.168.1.1` (this will never be your IP), put `192.168.1.1/1`
    1. Once created, go to the `Resources` tab and take note of the EC2 instance `Physical ID`. We will need this later
4. You're finished with AWS!

#### Instance Configuration
1. Copy your EC2 instance's public IP and take note of the location you saved our key pair `.pem` file to. Then, SSH into the EC2 instance with `ssh ubuntu@{PUBLIC_IP_ADDRESS} -i ./path/to/pem/file`
    * Having permissions issues due to a 'public key'? Run `chmod 400 ./path/to/pem/file` to fix this
1. Once connected, let's update our instance `sudo apt-get update`
1. Run `Java` and Ubuntu should give you a list of available packages. Install openjdk version 8 or above. For example, `sudo apt-get install openjdk-8-jre-headless`
1. Create a /opt folder if it does not already exist `mkdir /opt`
1. Make the user for our minecraft server `adduser --system --shell /bin/bash --home /opt/minecraft --group minecraft` and create a `server` directory in its home `mkdir /opt/minecraft/server`
1. Go to https://www.minecraft.net/en-us/download/server and find the link to download the latest Minecraft server jar file. Right click and `Copy Link Address`. In your EC2 instance, run `wget LINK_ADDRESS -P /opt/minecraft/server`. In my case, this is `wget https://launcher.mojang.com/v1/objects/4d1826eebac84847c71a77f9349cc22afd0cf0a1/server.jar -P /opt/minecraft/server`. You should now have a `server.jar` file in your server folder.
1. Accept the eula by creating a `eula.txt` file with `eula=true` as its contents. `echo "eula=true" >> /opt/minecraft/server/eula.txt`
1. Create the SystemD Unit file and set its contents to `/instance/minecraft.service` by `touch /etc/systemd/system/minecraft.service` and editing its contents
1. Enable the system file `systemctl enable minecraft.service`
1. Next, copy `instance/autoshutdown.py` and `instance/crontab` to your sudo home directory and run `sudo crontab /home/ubuntu/crontab -u ubuntu`. This will enable periodic player count checks and shutdown the server if it is idle for 5 minutes
1. The server should be available shortly at your server's public IP address on port 25565. View the server status by running `tail /opt/minecraft/server/logs/latest.log`

#### Web Server Configuration
1. Create a Heroku account and install the Heroku CLI
1. In your project directory, run `heroku create PROJECT_NAME`
1. Set the configuration variables with those that were noted earlier. Do this by filling in the following command or editing the configuration variables in your Herokuapp dashboard
    ```bash
    heroku config:set \
        AWS_ACCESS_KEY_ID=awsaccesskey \
        AWS_SECRET_ACCESS_KEY=awssecretaccesskey \
        INSTANCE_ID=instanceid \
        REGION_NAME=regionname \
        SERVER_PASSWORD=serverpassword
    ```
1. Push the project `git push heroku master`
1. The resulting URL will give you access to start the server

## Sources
* https://github.com/trevor-laher/OnDemandMinecraft
* https://minecraft.gamepedia.com/Tutorials/Server_startup_script
* https://wiki.vg/Server_List_Ping
* https://gist.github.com/MOZGIII/4529750
* https://gist.github.com/MarshalX/40861e1d02cbbc6f23acd3eced9db1a0