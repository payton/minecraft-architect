from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from mcstatus import MinecraftServer
import boto3
import logging
import time
import os

app = Flask(__name__)
CORS(app)

logger = logging.getLogger()

# Create session to access AWS environment
session = boto3.Session(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["REGION_NAME"]
)
# Create ec2 resource
ec2 = session.resource("ec2")


# Main endpoint for loading the webpage
@app.route('/')
def index():
    # Create instance object
    instance = ec2.Instance(os.environ["INSTANCE_ID"])
    if instance.state['Code'] == 16:
        # Attempt to ping Minecraft server... if failed, assume server is booting up
        try:
            lookup = MinecraftServer.lookup(instance.public_ip_address).query()
            server = {
                'status': 'online',
                'current_players': lookup.players.online,
                'max_players': lookup.players.max,
                'players': lookup.players.names,
                'ip': instance.public_ip_address + ':25565'
            }
        except Exception:
            server = {
                'status': 'starting',
                'ip': instance.public_ip_address + ':25565'
            }
    else:
        server = {
            'status': 'offline'
        }

    return render_template('index.html', server=server)


@app.route('/init', methods=['POST'])
def init_server_minecraft():
    input_pass = request.form['password']

    if input_pass == os.environ["SERVER_PASSWORD"]:
        logger.info("Password correct... initiating server startup")

        response = instance.start()
        state_code = instance.state['Code']

        # Wait until instance has completely started
        while not (state_code == 16):
            time.sleep(3)
            logger.info("Received AWS EC2 start response: {}".format(str(response)))
            state_code = instance.state['Code']
            logger.info("Server instance initiated: {}".format(instance))

        ip_address = instance.public_ip_address
        return jsonify({'login': True, 'ip': ip_address + ':25565'})
    else:
        logger.info("Password incorrect")
        return jsonify({'login': False})


if __name__ == "__main__":
    app.run()
