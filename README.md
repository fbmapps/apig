# API Gateway - v2020 APIG ^(>(oo)<)^
## Description
APIGW is a python app based on Flask, which served a Webhook to listen incoming requests from Webex Teams Client.

## Organization
All the files has the prefix **apigw_**
- __server__: The Flask Process. This script has the Flask process
- __webex__: Listener for Incoming Messages from Webex Teams. This script builds all the supported commands and send the list to the dispatcher
- __dispatcher__: Main script collecting incoming orders and calling Bot function to respond the requests
- __generic__: General Usage functions
- __logger__: The Audit record from the process
- __meraki__: a self contained Class and Functions, to expose Meraki API functions to configure and manage a meraki network via automation

## Usage
Several Environmental variables are required in order to use the APIGW
You need a Webex Teams account in order to be able to create a bot. Go to https://developer.webex.com
Once there you can create a Bot to obtain the following information:
### General Parameters
- __WEBEX_TEAMS_ACCESS_TOKEN__: The Token to connect the BOT to the APIGW
- __WEBEX_TEAMS_BOT_EMAIL__: BOT Email
- __WEBEX_TEAMS_BOT_NAME__: Bot Name, defined when you create the BOT 
### Bot Scope
In order to control the conversation access of the Bot and its scope, then you can retrieve the following parameters to attach the Bot to an specific Room
- __WEBEX_TEAMS_DIRECT_ROOM__: Room for 1:1 messaging
- __WEBEX_TEAMS_GROUP_ROOM__: Shared **spaces** where several user interact with the bot by calling it by name like @BotName
### Security Best Practices
- __WEBEX_ALLOWED_ORGANIZATION__: You use this to filter which organization is able to interact with the Bot.
- __WEBEX_WEBHOOK_SECRET_KEY__: This is a Preshare Key between Webhook and Flask Server in order to respond only when a match exist on the hashed data traversing from Webex Teams towards APIGW
- __allowed_users.yaml__: This files will have a list of the specifics User ID allowed to interact with the Bot, in order to avoid a change started by a non-authorized user. An example of the file structure has been provided.

### Meraki API Specific
- __MERAKI_API_KEY__: The Key allowing the Bot to Interact with Meraki API
- __MERAKI_ORG__: The Meraki Organization with the network to be managed
- __MERAKI_DEFAULT_NETWORK__: The default Network with the devices (MX Appliances, MS Switches, MR Access Points, MV Cameras and MC IP Phones)

#### Supported Meraki Actions
- __help__: Get Help
- __webex-health__: Get Health of Webex Teams Link
- __show-network__: Summary Info of Managed Meraki Network
- __show-vlans__: Display a List with the VLANS attached to the Meraki Network
- __show-switch__: Display a List with the Switches attached to the Meraki Network
- __change-port__: Parameters: Switch IP, Switch-Port, Vlan-ID ie change-port 1.1.1.1 10 101
- __activate-ssid__: Parameters: SSID Name, ie activate-ssid SSIDName
- __show-ssid__: Parameters: Display a List of All Enabled SSIDs
- __remove-ssid__: Parameters: Remove and Disable a SSIDs by name or Number ID ie remove-ssid |
- __show-ports__: Parameters: Display All Ports in a Switch show-ports
- __show-mx-ports__: Parameters: Display All Ports in a MX appliance show-mx-ports
- __disable-port__: Parameters: Deactivate Switch Port diasble-port

## Configuration
You can deploy the Flask Service behind a NGINX Reverse Proxy: This is a sample configuration

    server_name <your-web-server>;
    root /usr/share/nginx/html/<your-web-server>/public_html;

    location /apigw/ {

            proxy_pass http://127.0.0.1:5105/;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            client_max_body_size 5M;
    }

## Docker
This app can be deployed as a Docker container, but just deploying the docker-compose file.
Keep in mind you will need to provide the proper environmental variables files to be integrated into the container

To start just type
`docker-compose build && docker-compose up -d`

By Default the Docker Container exposed the port tcp/5105, but you can modify this

***
### Release
Created by frbello@cisco.com
[+]2020
(c)2020
@frbellom

